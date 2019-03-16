import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from picklefield.fields import PickledObjectField
from rest.models import Person
from django.core.exceptions import ValidationError


def validate_ip(ip_str):
    """FIXME: 检测ip合法性，debug测试未触发"""
    try:
        sep = ip_str.split('.')
        if len(sep) != 4:
            return False
        for i, x in enumerate(sep):
            int_x = int(x)
            if int_x < 0 or int_x > 255:
                return False
        return True
    except:
        return False


class Version(models.Model):
    content = PickledObjectField(null=True)

    class Meta:
        ordering = ('id',)


@receiver(post_save, sender=Person)
def post_save_person(sender, instance=None, created=False, **kwargs):
    content = {
        'created': set(),
        'updated': set(),
        'deleted': set()
    }
    if not instance.is_deleted:
        if created:
            content['created'].add(str(instance.uuid))
        else:
            content['updated'].add(str(instance.uuid))
    else:
        content['deleted'].add(str(instance.uuid))
    Version.objects.create(content=content)


class Device(models.Model):
    TYPE_CHOICES = (
        ('IN', '入'),
        ('OUT', '出'),
        ('UNKNOWN', '未设置'),
    )
    uuid = models.UUIDField(default=uuid.uuid1, unique=True, verbose_name='UUID')
    name = models.CharField(max_length=255, verbose_name='设备名', blank=True, null=True, unique=True)
    descriptions = models.TextField(verbose_name='设备信息', blank=True, null=True)
    device_type = models.CharField(max_length=255, choices=TYPE_CHOICES, default='UNKNOWN', verbose_name='设备类型')
    members = models.ManyToManyField(Person, related_name='devices')
    start_time = models.DateTimeField(verbose_name='开始运行时刻', default=now)
    latest_time = models.DateTimeField(verbose_name='最后运行时刻', default=now)
    position = models.CharField(max_length=255, verbose_name='设备位置', blank=True, null=True)
    ip = models.GenericIPAddressField(verbose_name='IP地址', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = '设备'
        verbose_name_plural = '设备列表'

    @property
    def urls(self):
        """FIXME: 需要获取URL，暂时没有好的方法"""
        return {
            'detail': reverse('sync:device-detail', kwargs={'pk': self.pk}),
            'update': reverse('sync:device-update', kwargs={'pk': self.pk}),
            'delete': reverse('sync:device-delete', kwargs={'pk': self.pk}),
        }
