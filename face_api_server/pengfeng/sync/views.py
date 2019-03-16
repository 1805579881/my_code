import datetime
import json
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView)

from rest.models import Person, Record
from sync.models import Device, Version
from sync.serializers import DeviceSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from .sync_tool import calculate_difference
from django.conf import settings

DEVICE_TIME_LIMIT = settings.DEVICE_TIME_LIMIT if hasattr(settings, 'DEVICE_TIME_LIMIT') else 3
logger = logging.getLogger(__name__)
tz = timezone.get_current_timezone()


def get_device_uuid_from_request(request):
    device_uuid = None
    if 'HTTP_DEVICE_ID' in request.META:
        device_uuid = request.META.get('HTTP_DEVICE_ID')
    elif 'DEVICE_ID' in request.META:
        device_uuid = request.META.get('DEVICE_ID')
    return device_uuid


@require_http_methods(["GET"])
def get_version_difference(request):
    try:
        logger.info('开始处理数据同步请求')

        logger.info('获取版本信息')
        version = Version.objects.last()
        current_version = request.GET.get('current_version')
        system_version = version.id if version else None
        logger.debug('请求版本为{0}，系统版本为{1}'.format(current_version, system_version))
        logger.info('获取版本信息成功')

        logger.info('开始解析数据')
        device_uuid = get_device_uuid_from_request(request)
        logger.debug('设备UUID为{}'.format(device_uuid))
        if device_uuid is None:
            raise Exception('请求头部不包含设备UUID')
        logger.info('解析数据成功')

        logger.info('开始计算{current}-{system}版本差异'.format(current=current_version, system=system_version))
        result = calculate_difference(int(current_version) if current_version else None, system_version, device_uuid)
        logger.info('版本差异计算成功')

        logger.info('数据同步请求处理成功')
    except ValueError:
        result = {
            'error': True,
            'detail': '版本号必须是一个整数'
        }
        logger.exception('版本号必须是一个整数')
    except Exception as e:
        result = {
            'error': True,
            'detail': str(e)
        }
        logger.exception('数据同步请求处理失败')
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(["POST"])
def create_or_update_device(request):
    try:
        logger.info('开始处理设备请求')

        logger.info('验证HTTP HEADER')
        logger.debug('HEADER数据类型为{}'.format(request.content_type))
        if request.content_type != 'application/json':
            raise Exception('HTTP请求头只能为application/json')
        logger.info('验证HTTP HEADER成功')

        logger.info('开始解析数据')
        data = json.loads(request.body.decode('utf-8'), encoding='utf-8')
        logger.debug('数据内容为{}'.format(data))
        logger.info('解析数据成功')

        logger.info('验证数据')
        device_info = data.get('device_info')
        if not device_info:
            raise Exception('设备信息为空')
        if not all(key in device_info for key in ('uuid', 'name', 'position', 'device_type')):
            raise Exception('设备信息不全')
        if device_info['device_type'] not in ('IN', 'OUT'):
            raise Exception('设备类型错误，不能为{}'.format(device_info['device_type']))
        logger.info('验证数据成功')

        logger.info('更新设备信息')
        if Device.objects.filter(uuid=device_info['uuid']).exists():
            device = Device.objects.get(uuid=device_info['uuid'])
            device.name = device_info['name']
            device.position = device_info['position']
            device.device_type = device_info['device_type']
            device.ip = request.META.get('REMOTE_ADDR')
            device.save()
            created = False
        else:
            Device.objects.create(uuid=device_info['uuid'], name=device_info['name'], position=device_info['position'],
                                  device_type=device_info['device_type'], ip=request.META.get('REMOTE_ADDR'))
            created = True
        if created:
            logger.info('创建新设备{}'.format(device_info['uuid']))
        logger.info('更新设备信息成功')

        result = {
            'error': False
        }
        logger.info('设备请求处理成功')
    except Exception as e:
        result = {
            'error': True,
            'detail': str(e)
        }
        logger.exception('设备请求处理失败')
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(["POST"])
def upload_record(request):
    try:
        logger.info('开始上传匹配记录')

        logger.info('验证HTTP HEADER')
        logger.debug('HEADER数据类型为{}'.format(request.content_type))
        if request.content_type != 'application/json':
            raise Exception('HTTP请求头只能为application/json')
        logger.info('验证HTTP HEADER成功')

        logger.info('验证设备信息')
        device_uuid = get_device_uuid_from_request(request)
        logger.debug('设备UUID为{}'.format(device_uuid))
        if device_uuid is None:
            raise Exception('请求头部不包含设备UUID')
        device = Device.objects.get(uuid=device_uuid)
        logger.info('验证设备信息成功')

        logger.info('开始解析数据')
        data = json.loads(request.body.decode('utf-8'), encoding='utf-8')
        logger.debug('数据内容为{}'.format(data))
        logger.info('解析数据成功')

        logger.info('验证数据')
        records = data.get('records')
        if not records:
            raise Exception('匹配记录为空')
        logger.info('验证数据成功')

        logger.info('开始保存匹配记录')
        warnings = {'unmatched': []}
        for item in records:
            if Person.objects.filter(uuid=item['uuid']).exists():
                with transaction.atomic():
                    person = Person.objects.get(uuid=item['uuid'])
                    bulk_records = []
                    for timestamp in item['mills']:
                        created = datetime.datetime.fromtimestamp(float(timestamp), tz=tz)
                        bulk_records.append(Record(target=person, created=created, record_type=device.device_type))
                    Record.objects.bulk_create(bulk_records)
            else:
                logger.warning('人员{uuid}不匹配'.format(uuid=item['uuid']))
                warnings['unmatched'].append(item['uuid'])
        logger.info('匹配记录保存成功')

        result = {
            "error": False,
        }
        if warnings['unmatched']:
            result['warning'] = warnings
        logger.info('匹配记录上传成功')
    except Device.DoesNotExist:
        result = {
            'error': True,
            'detail': '找不到设备'
        }
        logger.exception('找不到设备')
    except Exception as e:
        result = {
            'error': True,
            'detail': str(e)
        }
        logger.exception('匹配记录上传失败')
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(["POST"])
def heart_beats(request):
    try:
        logger.info('开始处理心跳请求')

        logger.info('验证HTTP HEADER')
        logger.debug('HEADER数据类型为{}'.format(request.content_type))
        if request.content_type != 'application/json':
            raise Exception('HTTP请求头只能为application/json')
        logger.info('验证HTTP HEADER成功')

        logger.info('开始解析数据')
        device_uuid = get_device_uuid_from_request(request)
        logger.debug('设备UUID为{}'.format(device_uuid))
        if device_uuid is None:
            raise Exception('请求头部不包含设备UUID')
        logger.info('解析数据成功')

        logger.info('查询设备')
        device = Device.objects.get(uuid=device_uuid)
        logger.info('查询设备成功')

        logger.info('提取设备IP信息')
        ip = request.META.get('REMOTE_ADDR')
        logger.info('提取设备IP信息成功')

        logger.info('计算时间参数')
        now = datetime.datetime.now(tz=tz)
        if abs((now - device.latest_time).total_seconds()) > DEVICE_TIME_LIMIT:
            device.start_time = now
        device.latest_time = datetime.datetime.now(tz=tz)
        device.save()
        logger.info('计算时间参数成功')

        logger.info('发布连接信息')
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'monitor',
            {
                'type': 'device_info_message',
                'device_info': {
                    'name': device.name,
                    'device_type': device.device_type,
                    'ip': ip,
                    'uuid': str(device.uuid),
                    'online_time': str(device.latest_time - device.start_time),
                    'latest': datetime.datetime.now(tz=tz).strftime('%Y-%m-%d %H:%M:%S'),
                    'urls': device.urls,
                    'position': device.position
                }
            }
        )
        logger.info('发布连接信息成功')

        result = {
            'error': False
        }
        logger.info('心跳请求处理成功')
    except Device.DoesNotExist:
        result = {
            'error': True,
            'detail': '设备信息无效，找不到设备'
        }
        logger.exception('设备信息无效，找不到设备')
    except Exception as e:
        result = {
            'error': True,
            'detail': str(e)
        }
        logger.exception('心跳保持失败')
    return JsonResponse(result)


@method_decorator(login_required, name='dispatch')
class DeviceListView(TemplateView):
    template_name = 'sync/device_list.html'


@method_decorator(login_required, name='dispatch')
class DeviceCreateView(CreateView):
    model = Device
    template_name = 'sync/device_create.html'
    fields = ['uuid', 'name', 'device_type', 'position', 'ip', 'descriptions']

    def get_success_url(self):
        return reverse_lazy('sync:device-update', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class DeviceUpdateView(UpdateView):
    model = Device
    template_name = 'sync/device_update.html'
    fields = ['uuid', 'name', 'device_type', 'position', 'ip', 'descriptions']
    success_url = reverse_lazy('sync:device-list')

    def get_context_data(self, **kwargs):
        current_people = self.object.members.all().values_list('pk', flat=True)
        groups = {}
        for position in set(
                Person.objects.filter(Q(is_active=True) & Q(is_deleted=False)).values_list('position', flat=True)):
            group_people = [{
                'pk': person.pk,
                'selected': True if person.pk in current_people else False,
                'name': person.name,
                'position': person.position,
                'employee_number': person.employee_number,
                'department': person.department.name
            } for person in Person.objects.filter(Q(is_active=True) & Q(position=position) & Q(is_deleted=False))]
            groups[position] = group_people
        people = [{
            'pk': person.pk,
            'selected': True if person.pk in current_people else False,
            'name': person.name,
            'position': person.position,
            'employee_number': person.employee_number,
            'department': person.department.name
        } for person in Person.objects.filter(Q(is_active=True) & Q(is_deleted=False))]
        context = super().get_context_data(**kwargs)
        context['people'] = people
        context['groups'] = groups
        return context


@method_decorator(login_required, name='dispatch')
class DeviceDeleteView(DeleteView):
    model = Device
    template_name = 'sync/device_delete.html'
    success_url = reverse_lazy('sync:device-list')


@method_decorator(login_required, name='dispatch')
class DeviceDetailView(DetailView):
    model = Device
    template_name = 'sync/device_detail.html'


@csrf_exempt
@require_http_methods(["POST"])
def set_people(request):
    try:
        device_pk = request.POST.get('device_pk')
        people_pks = request.POST.getlist('people')
        device = Device.objects.get(pk=device_pk)

        logger.info('开始关联人员列表')
        with transaction.atomic():
            logger.info('绑定设备与人员')
            people = Person.objects.filter(id__in=people_pks)
            device.members.clear()
            for person in people:
                device.members.add(person)
            device.save()
            logger.info('系统数据版本递增')
            people_uuid_list = Person.objects.filter(id__in=people_pks).values_list('uuid', flat=True)
            content = {
                'created': set(),
                'updated': set(),
                'deleted': set()
            }
            content['updated'].update(people_uuid_list)
            Version.objects.create(content=content)
        logger.info('关联人员列表完成')
        result = {'result': True}
    except BaseException:
        result = {'result': False}
        logger.exception('无法关联人员列表')
    return JsonResponse(result)


@method_decorator(login_required, name='dispatch')
class LoggingView(TemplateView):
    template_name = 'sync/logging.html'


class DeviceViewSet(ReadOnlyModelViewSet):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()
    lookup_field = 'uuid'
