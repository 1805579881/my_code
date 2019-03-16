import logging
from functools import lru_cache

from django.db.models import Q

from rest.models import Person
from sync.models import Device
from .models import Version

logger = logging.getLogger(__name__)


def compare(current_version, system_version):
    logger.info('开始匹配处理逻辑')
    if system_version is None:
        raise Exception('服务器无可用版本')
    if current_version is None:
        handler_name = 'batch'
    elif system_version == current_version:
        handler_name = 'same'
    elif system_version > current_version:
        handler_name = 'incremental'
    else:
        raise Exception('当前版本号大于服务器版本号')
    logger.info('匹配处理逻辑成功，当前处理函数为{}'.format(handler_name))
    return handler_name


def same_handle(current_version, system_version, device_uuid):
    """设备版本号与服务器一致，不需要同步数据"""
    result = {
        'error': False,
        'is_latest': True,
        'current_version': system_version
    }
    logger.info('设备版本号与服务器一致，不需要同步数据')
    return result


def get_deleted_person_with_device_uuid(device_uuid):
    """选取绑定人员中所有没有被删除，且在职的员工的补集进行屏蔽"""
    device = Device.objects.get(uuid=device_uuid)
    validated_people = device.members.filter(Q(is_deleted=False) & Q(is_active=True)).values_list('uuid', flat=True)
    deleted_people = set(str(person.uuid) for person in Person.objects.exclude(uuid__in=validated_people))
    return deleted_people


def incremental_handle(current_version, system_version, device_uuid):
    """
    对应updated.json中的内容，共有6种情况：增加且修改（增）、增加且删除（移除）、增加（增）、修改（改）、修改且删除（删除）、删除（删除）。
    C对应增加的集合，U对应修改的集合，D对应删除的集合
    计算步骤为：获取基础差异信息->优化差异信息->整合差异信息->整合设备差异信息->数据库取数据->返回结果
    """
    logger.info('开始获取设备绑定人员')
    device_deleted = get_deleted_person_with_device_uuid(device_uuid)
    logger.info('需要屏蔽的人员为{}'.format(device_deleted))
    logger.info('获取设备绑定人员成功')

    logger.info('获取{current}-{system}基础差异信息'.format(current=current_version, system=system_version))
    versions = Version.objects.filter(Q(id__gt=current_version) & Q(id__lte=system_version))
    created = set()
    updated = set()
    deleted = set()
    for version in versions:
        if version.content:
            created.update(version.content['created'])
            updated.update(version.content['updated'])
            deleted.update(version.content['deleted'])

    logger.info('优化{current}-{system}差异信息'.format(current=current_version, system=system_version))
    final_created = created.difference(deleted)
    final_deleted = deleted.difference(created)
    final_updated = updated.difference(created).difference(deleted)
    final_removed = created.intersection(deleted)

    logger.info('整合{current}-{system}差异信息'.format(current=current_version, system=system_version))
    final_created.difference_update(final_removed)
    final_deleted.difference_update(final_removed)
    final_updated.difference_update(final_removed)

    logger.info('整合设备{}差异信息'.format(device_uuid))
    final_created.difference_update(device_deleted)
    final_updated.difference_update(device_deleted)
    final_deleted.update(device_deleted)

    logger.info('开始获取员工详细信息')
    result = {
        'error': False,
        'is_latest': False,
        'current_version': system_version,
        "clear": False,
        'created': [{
            'uuid': str(person.uuid),
            'name': person.name,
            'position': person.position,
            'image': person.image,
            'employment_date': person.employment_date,
            'employee_number': person.employee_number
        } for person in Person.objects.filter(
            Q(image__isnull=False) & Q(uuid__in=final_created) & Q(is_active=True) & Q(is_deleted=False))],
        'updated': [{
            'uuid': str(person.uuid),
            'name': person.name,
            'position': person.position,
            'image': person.image,
            'employment_date': person.employment_date,
            'employee_number': person.employee_number
        } for person in Person.objects.filter(
            Q(image__isnull=False) & Q(uuid__in=final_updated) & Q(is_active=True) & Q(is_deleted=False))],
        'deleted': [key for key in final_deleted],
    }
    logger.info('员工详细信息获取成功')
    return result


def batch_handle(_, system_version, device_uuid):
    """同步所有绑定到设备的人员数据"""
    logger.info('开始获取设备绑定人员')
    device_deleted = get_deleted_person_with_device_uuid(device_uuid)
    logger.info('需要屏蔽的人员为{}'.format(device_deleted))
    updated = []
    deleted = list(device_deleted)
    logger.info('获取设备绑定人员成功')

    logger.info('开始获取员工详细信息')
    # 只推送有照片的在职人员
    people = Person.objects.filter(Q(image__isnull=False) & Q(is_active=True) & Q(is_deleted=False)).exclude(
        uuid__in=device_deleted)
    created = [{
        'uuid': str(person.uuid),
        'name': person.name,
        'position': person.position,
        'image': person.image,
        'employment_date': person.employment_date,
        'employee_number': person.employee_number
    } for person in people]
    result = {
        'error': False,
        'is_latest': False,
        'current_version': system_version,
        "clear": True,
        'created': created,
        'updated': updated,
        'deleted': deleted,
    }
    logger.info('员工详细信息获取成功')
    return result


handlers = {
    'batch': batch_handle,
    'incremental': incremental_handle,
    'same': same_handle
}


@lru_cache(maxsize=256, typed=False)
def calculate_difference(current_version, system_version, device_uuid):
    logger.info('开始对比版本号')
    handler_name = compare(current_version, system_version)
    logger.info('版本号对比成功')
    handler = handlers.get(handler_name)
    if handler:
        logger.info('处理版本差异')
        result = handler(current_version, system_version, device_uuid)
        logger.debug('差异数据为{}'.format(result))
        logger.info('版本差异处理成功')
        return result
    else:
        raise Exception('没有合适的函数处理数据差异')
