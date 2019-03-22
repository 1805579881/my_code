# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse,redirect
from face_veri_pose_cd import  get_feature_out_gpu_set
from pair.models import det, landmark_p, recog, align
from models import PeopleInfo
import os
import threading
import base64
import numpy as np
import cv2
import logging
# Create your views here.
lock = [threading.Lock() for i in range(4)]
device_id = int(os.environ.get('DEVICE_ID',1))


def create_info(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)
        image = request.FILES.get("image", None)
        if not name:
            return HttpResponse("未获取信息的姓名，姓名为必填项，请刷新页面重试")
        if not image:
            return HttpResponse("未获取到上传的照片，照片为必填项，请刷新页面重试")
        image_name = image.name.encode("utf16")
        print image_name, type(image_name)
        image_name,image_ass = image_name.rsplit('.')
        print image_name,image_ass
        image_bytes = image.read()
        image_base64 = base64.b64encode(image_bytes)
        img = cv2.imdecode(np.fromstring(image_base64, np.uint8), cv2.IMREAD_COLOR)
        global device_id
        # 获取线程锁
        lock[device_id].acquire()
        try:
            #  获取特征值
            check_flag, feature = get_feature_out_gpu_set(image, det, landmark_p, recog,
                                                           align, device_id)
            print feature,"feature+++"
            is_create = PeopleInfo.objects.create(name=name,image=image,image_base64=image_base64,feature=feature)
            print is_create
            if is_create:
                return  HttpResponse(u'信息存储成功')
        except Exception as e:
            return HttpResponse(u"获取特征值失败，请稍后重试")

        finally:
            # 释放线程锁
            lock[device_id].release()
