# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from uuid import uuid1
# Create your models here.

class PeopleInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name=u"姓名")
    number = models.CharField(max_length=255, default=uuid1, unique=True, verbose_name=u"编号")
    # BinaryField 能存储base64加密文件
    image_base64 = models.BinaryField(null=True, verbose_name=u"Base64编码图片")
    image = models.ImageField(
        upload_to='info_management/image', null=True, blank=True,
        verbose_name=u"照片"
    )
    feature = models.CharField(max_length=255, verbose_name="特征值")

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = u"人员信息"
        verbose_name_plural = verbose_name