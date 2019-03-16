# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import date
from datetime import datetime
from uuid import uuid1
from django.core.exceptions import ValidationError
from django.urls import reverse
import logging
import numpy as np
from PIL import Image
import base64
from io import BytesIO

# Create your models here.
logger = logging.getLogger(__name__)


def get_random_base64_image_str():
    img_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
    buffer = BytesIO()
    img.save(buffer, format="png")
    img_str = base64.b64encode(buffer.getvalue())
    return img_str.decode('ascii')


class PeopleInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name=u"姓名")
    number = models.CharField(max_length=255, default=uuid1, unique=True, verbose_name=u"编号")
    # BinaryField 能存储base64加密文件
    image_base64 = models.BinaryField(null=True, verbose_name=u"Base64编码图片")
    image = models.ImageField(
        upload_to='info_management/image', null=True, blank=True,
        verbose_name=u"照片"
    )

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = u"员工信息"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.image and not self.image_base64:
            logger.error('找不到图片')
            raise ValidationError('未上传图片')

        if self.image:
            print '执行图片编码'
            try:
                image_bytes = self.image.read()
                images = base64.b64encode(image_bytes)
                img_str = images.encode('utf-8')

            except Exception:
                logger.exception('{}图片转化为base64字符串失败'.format(self.number))
                self.image = None
                img_str = get_random_base64_image_str()
            self.image_base64 = img_str

        super(PeopleInfo, self).save(**kwargs)


class MatchingRecord(models.Model):
    record_time = models.TimeField(default=datetime.now(), verbose_name=u"匹配时间")
    type = models.CharField(max_length=7, choices=(("IN", u"入"), ("OUT", u"出"), ('UNKNOWN', u'未设置')),
                            verbose_name=u"匹配记录", default='UNKNOWN')
    peoples = models.ForeignKey(to=PeopleInfo, on_delete=models.DO_NOTHING, verbose_name=u"匹配人员")

    class Meta:
        verbose_name = "匹配记录"
        verbose_name_plural = verbose_name