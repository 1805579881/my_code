import base64
import logging
import uuid
from datetime import date, datetime, timedelta
from uuid import uuid1
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from business_calendar import Calendar, MO, TU, WE, TH, FR, SA

weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
cal = Calendar(workdays=[MO, TU, WE, TH, FR, SA])


def get_random_base64_image_str():
    img_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
    buffer = BytesIO()
    img.save(buffer, format="png")
    img_str = base64.b64encode(buffer.getvalue())
    return img_str.decode('ascii')


tz = timezone.get_current_timezone()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        logger.info('新建用户，创建用户令牌')
        Token.objects.create(user=instance)
        logger.info('用户令牌创建成功')


class Department(models.Model):
    name = models.CharField(max_length=255, default='UNKNOWN')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        verbose_name = '部门管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @property
    def urls(self):
        """FIXME: 需要获取URL，暂时没有好的方法"""
        return ','.join([
            reverse('enhanced_ui:department-detail', kwargs={'pk': self.pk}),
            reverse('enhanced_ui:department-update', kwargs={'pk': self.pk}),
            reverse('enhanced_ui:department-delete', kwargs={'pk': self.pk})
        ])

    def delete(self, using=None, keep_parents=False, **kwargs):
        depart = Person.objects.filter(Q(is_deleted=False) & Q(department__name=self.name))
        if depart.count() >= 1:
            raise ValidationError('此部门还有人员，请先删除人员')
        if not self.is_deleted:
            self.is_deleted = True
            #self.save()
            super(Department, self).save(**kwargs)
        else:
            raise ValidationError('无法删除已离线的部门')

    # def save(self, **kwargs):
    #     ""很有借鉴意义的方法，建议不要删除，方便做参考"""
    #     if self.id == None:
    #         super(Department, self).save(**kwargs)
    #     else:
    #         if self.is_deleted:
    #             depart_name = Department.objects.get(id=self.id).name
    #             people_1 = Person.objects.filter(department=depart_name)
    #             for person in people_1:
    #                 person.department = None
    #                 person.save()
    #             super(Department, self).save(**kwargs)
    #             people_2 = Person.objects.filter(department=None)
    #             depart_temp = Department.objects.get(id=self.id)
    #             for person in people_2:
    #                 person.department = depart_temp
    #                 person.save()
    #         else:
    #             super(Department, self).save(**kwargs)


class Person(models.Model):
    uuid = models.UUIDField(default=uuid1, unique=True)
    name = models.CharField(max_length=255, verbose_name='姓名')
    position = models.CharField(max_length=255, verbose_name='职位')
    # FIXME: 工号为唯一识别标志，应变成unique
    employee_number = models.CharField(max_length=255, verbose_name='工号', default=uuid1)
    image = models.TextField(verbose_name='Base64编码图片', null=True)
    raw_image = models.ImageField(verbose_name='照片', upload_to='img', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='是否激活', help_text='未激活即为离职状态')
    employment_date = models.DateField(default=date.today, verbose_name='入职时间')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='部门',
                                   related_name='department_name', null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True, verbose_name='离职时间')

    def date_range_report(self, start_date, end_date):
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        date_range = end_datetime - start_datetime
        result = []
        all_records = Record.objects.filter(target=self, created__gte=start_datetime, created__lte=end_datetime,
                                            record_type__in=['IN', 'OUT'])
        attended_days = 0
        absent_days = 0
        additional_days = 0
        for i in range(date_range.days + 1):
            current_date = start_datetime + timedelta(days=i)
            is_workday = cal.isworkday(current_date.astimezone(tz))
            records = all_records.filter(created__year=current_date.year, created__month=current_date.month,
                                         created__day=current_date.day)
            if records.exists():
                attended = True
            else:
                attended = False
            records_in = records.filter(record_type='IN').order_by('created')
            records_out = records.filter(record_type='OUT').order_by('-created')
            record_in = None
            record_out = None
            if records_in.exists():
                record_in = records_in.first()
            if records_out.exists():
                record_out = records_out.first()
            if attended:
                attended_days += 1
                if not is_workday:
                    additional_days += 1
            elif is_workday:
                absent_days += 1
            if is_workday:
                if attended:
                    table_class = 'table-success'
                else:
                    table_class = 'table-danger'
            else:
                table_class = 'table-info'
            result.append(
                {
                    'in': record_in.created.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') if record_in else '--',
                    'out': record_out.created.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') if record_out else '--',
                    'attended': attended,
                    'date': current_date.astimezone(tz).strftime('%Y-%m-%d'),
                    'is_workday': is_workday,
                    'table_class': table_class,
                    'weekday': weekdays[current_date.weekday()],
                    'overtime': True if attended and not is_workday else False
                }
            )
        return attended_days, absent_days, additional_days, result[::-1]

    @property
    def report(self):
        today = datetime.now()
        result = []
        for i in range(1, 31):
            current_date = today - timedelta(days=i)
            records = Record.objects.filter(target=self, created__year=current_date.year,
                                            created__month=current_date.month, created__day=current_date.day,
                                            record_type__in=['IN', 'OUT'])
            if records.exists():
                attended = True
            else:
                attended = False
            records_in = records.filter(record_type='IN').order_by('created')
            records_out = records.filter(record_type='OUT').order_by('-created')
            record_in = None
            record_out = None
            if records_in.exists():
                record_in = records_in.first()
            if records_out.exists():
                record_out = records_out.first()
            result.append(
                {
                    'in': record_in.created.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') if record_in else '--',
                    'out': record_out.created.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') if record_out else '--',
                    'attended': '是' if attended else '否',
                    'date': current_date.astimezone(tz).strftime('%Y-%m-%d')
                }
            )
        return result

    @property
    def urls(self):
        """FIXME: 需要获取URL，暂时没有好的方法"""
        return ','.join([
            reverse('enhanced_ui:face-detail', kwargs={'pk': self.pk}),
            reverse('enhanced_ui:face-update', kwargs={'pk': self.pk}),
            reverse('enhanced_ui:face-delete', kwargs={'pk': self.pk})
        ])

    def __str__(self):
        return '{0}-{1}-{2}'.format(self.name, self.position, self.employee_number)

    def clean(self):
        if not self.is_deleted and Person.objects.filter(
                Q(employee_number=self.employee_number) & Q(is_deleted=False)).exclude(uuid=self.uuid).exists():
            raise ValidationError('工号重复，无法保存')
        super(Person, self).clean()

    def save(self, **kwargs):
        if self.department.is_deleted:
            raise ValidationError('部门已删除')
        if not self.image and not self.raw_image:
            logger.error('找不到图片')
            raise ValidationError('未上传图片')
        if self.raw_image:
            try:
                image_bytes = self.raw_image.read()
                image = base64.b64encode(image_bytes)
                img_str = image.decode('utf-8')
            except Exception:
                logger.exception('人员{}图片转化为base64字符串失败'.format(self.employee_number))
                self.raw_image = None
                img_str = get_random_base64_image_str()
            self.image = img_str

        super(Person, self).save(**kwargs)

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            self.is_deleted = True
            self.save()
        else:
            raise ValidationError('无法删除已离线的员工')

    class Meta:
        ordering = ('-is_active', 'name', 'position', 'employee_number', 'employment_date', 'departure_date',)
        verbose_name = '人员'
        verbose_name_plural = '人员列表'


class Record(models.Model):
    TYPE_CHOICES = (
        ('IN', '入'),
        ('OUT', '出'),
        ('UNKNOWN', '未设置'),
    )
    uuid = models.UUIDField(default=uuid.uuid1, unique=True)
    created = models.DateTimeField(verbose_name='记录时间')
    target = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name='records', verbose_name='匹配目标')
    record_type = models.CharField(max_length=255, choices=TYPE_CHOICES, default='UNKNOWN')

    class Meta:
        ordering = ('-created', 'target', 'record_type')
        verbose_name = '匹配记录'
        verbose_name_plural = '匹配记录列表'
