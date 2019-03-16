import base64
import json
import logging
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView
from pyzip import PyZip

from enhanced_ui.forms import FaceDataBatchUploadForm
from rest.models import Person, Department
from sync.models import Device, Version
from openpyxl import load_workbook
from io import BytesIO
import base64

tz = timezone.get_current_timezone()
logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class FaceListView(ListView):
    model = Person
    template_name = 'enhanced_ui/face_list.html'
    queryset = Person.objects.filter((Q(raw_image__isnull=False) | Q(image__isnull=False)) & Q(is_deleted=False))


@method_decorator(login_required, name='dispatch')
class FaceCreateView(CreateView):
    model = Person
    template_name = 'enhanced_ui/face_create.html'
    fields = ['name', 'position', 'employee_number', 'raw_image', 'is_active', 'employment_date', 'departure_date', 'department']


    def get_success_url(self):
        return reverse_lazy('enhanced_ui:face-update', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        depart = Department.objects.filter(is_deleted=False)
        context = super().get_context_data(**kwargs)
        context['depart'] = depart
        return context


@method_decorator(login_required, name='dispatch')
class FaceUpdateView(UpdateView):
    model = Person
    template_name = 'enhanced_ui/face_update.html'
    fields = ['name', 'position', 'employee_number', 'raw_image', 'is_active', 'employment_date', 'departure_date', 'department']

    def get_success_url(self):
        return reverse_lazy('enhanced_ui:face-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        current_devices = [device.pk for device in self.object.devices.all()]
        devices = [{
            'pk': device.pk,
            'selected': True if device.pk in current_devices else False,
            'name': device.name,
            'device_type': device.device_type
        } for device in Device.objects.all()]
        context = super().get_context_data(**kwargs)
        context['devices'] = devices
        return context


@method_decorator(login_required, name='dispatch')
class FaceDeleteView(DeleteView):
    model = Person
    template_name = 'enhanced_ui/face_delete.html'
    success_url = reverse_lazy('enhanced_ui:face-list')


@method_decorator(login_required, name='dispatch')
class FaceDetailView(DetailView):
    model = Person
    template_name = 'enhanced_ui/face_detail.html'


class Item:
    def __init__(self):
        self.info = None
        self.base64_image = None

    def is_valid(self):
        if self.info and self.base64_image:
            return True
        else:
            return False


def validate_excel(work_book):
    info_list = list(work_book['员工信息'].values)
    if info_list[0] != ('工号', '姓名', '所属部门', '职位', '在职状态', '入职时间'):
        logger.debug('excel列标题为{}'.format(info_list[0]))
        raise Exception('列标题错误，当前列标题为{}'.format(info_list[0]))
    for idx, info in enumerate(info_list):
        logger.debug('excel第{0}行内容为标题为{1}'.format(idx + 1, info))
        if len(info) != 6:
            raise Exception('第{0}行人员信息错误，当前行内容为{1}'.format(idx + 1, info))


def read_people_from_zip_file(zip_bytes):
    logger.info('开始读取zip文件')
    pyzip = PyZip().from_bytes(zip_bytes)
    contents = pyzip.zip_content
    logger.debug('zip文件中包含{}'.format(contents.keys()))

    if 'info.xlsx' in contents:
        logger.info('读取excel文件')
        wb = load_workbook(filename=BytesIO(contents['info.xlsx']))

        logger.info('  ')
        validate_excel(wb)

        logger.info('解析表格数据')
        info_list = list(wb['员工信息'].values)
        people = []
        for idx, person in enumerate(info_list):
            if idx >= 1:
                depart = Department.objects.get(Q(name=person[2]) & Q(is_deleted=False))
                item = Item()
                item.info = {
                    '工号': person[0],
                    '姓名': person[1],
                    '所属部门': depart,
                    '职位': person[3],
                    '在职状态': person[4],
                    '入职时间': person[5]
                }
                image_prefix = item.info['工号']
                if '{}.jpg'.format(image_prefix) in contents or '{}.png'.format(image_prefix) in contents:
                    if '{}.jpg'.format(image_prefix) in contents:
                        image = base64.b64encode(contents['{}.jpg'.format(image_prefix)])
                    else:
                        image = base64.b64encode(contents['{}.png'.format(image_prefix)])
                    item.base64_image = image.decode('utf-8')
                    people.append(item)
                else:
                    raise Exception('缺少工号为{0}的员工图片'.format(image_prefix))
        return people
    else:
        raise Exception('找不到info.xlsx')


@method_decorator(login_required, name='dispatch')
class BatchUpload(FormView):
    form_class = FaceDataBatchUploadForm
    template_name = 'enhanced_ui/face_batch_create.html'
    success_url = reverse_lazy('enhanced_ui:face-list')

    def form_valid(self, form):
        try:
            validated_people = []
            people = read_people_from_zip_file(form.cleaned_data['file'].read())
            for person in people:
                if person.is_valid():
                    employee_number = person.info['工号']
                    if Person.objects.filter(employee_number=employee_number, is_deleted=False).exists():
                        messages.warning(self.request,
                                         '该员工已存在\n{}，已经跳过'.format(
                                             json.dumps(person.info, ensure_ascii=False, indent=4)))
                    else:
                        validated_people.append(person)
            with transaction.atomic():
                created = [str(uuid.uuid1()) for _ in range(len(validated_people))]
                bulk = [
                    Person(name=person.info['姓名'], position=person.info['职位'], employee_number=person.info['工号'],
                           image=person.base64_image, uuid=created[idx], is_active=person.info['在职状态'],
                           employment_date=person.info['入职时间'], department=person.info['所属部门']) for
                    idx, person in enumerate(validated_people)]
                Person.objects.bulk_create(bulk)
                content = {
                    'created': set(created),
                    'updated': set(),
                    'deleted': set()
                }
                Version.objects.create(content=content)
            return super(BatchUpload, self).form_valid(form)
        except Exception as e:
            messages.error(self.request, '文件错误，无法导入\n{0}'.format(str(e)))
            return self.render_to_response(self.get_context_data(form=form))


@csrf_exempt
@require_http_methods(["POST"])
def delete_selected_people(request):
    try:
        logger.info('获取待删除人员列表')
        pks = request.POST.getlist('pks[]')
        logger.debug('待删除人员为{}'.format(pks))

        logger.info('开始删除数据')
        with transaction.atomic():
            logger.info('更新人员删除标志位')
            Person.objects.filter(id__in=pks).update(is_deleted=True)

            logger.info('更新服务器版本')
            deleted = map(str, Person.objects.filter(id__in=pks).values_list('uuid', flat=True))
            content = {
                'created': set(),
                'updated': set(),
                'deleted': set()
            }
            content['deleted'].update(deleted)
            Version.objects.create(content=content)
            logger.debug('服务器新增版本内容为{}'.format(content))
        result = {'error': False}
        logger.info('数据软删除成功')
    except Exception as e:
        result = {
            'error': True,
            'detail': str(e)
        }
        logger.exception('删除数据失败')
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(["POST"])
def set_devices(request):
    try:
        logger.info('获取人员信息和设备列表')
        person_pk = request.POST.get('person_pk')
        device_pks = request.POST.getlist('devices')
        logger.debug('人员pk为{0}，待绑定设备为{1}'.format(person_pk, device_pks))

        logger.info('获取人员{}信息'.format(person_pk))
        person = Person.objects.get(pk=person_pk)

        logger.info('开始设置推送设备')
        with transaction.atomic():
            logger.info('绑定设备信息')
            devices = Device.objects.filter(id__in=device_pks)
            person.devices.clear()
            person.devices.add(*devices)

            logger.info('更新服务器版本')
            content = {
                'created': set(),
                'updated': set(),
                'deleted': set()
            }
            content['updated'].add(str(person.uuid))
            Version.objects.create(content=content)
        result = {
            'error': False
        }
        logger.info('推送设备设置完成')
    except Exception as e:
        result = {
            'error': True,
            'detail': str(e)
        }
        logger.exception('无法设置推送设备')
    return JsonResponse(result)
