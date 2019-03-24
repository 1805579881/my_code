# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse,redirect
from face_veri_pose_cd import  get_feature_out_gpu_set
from pair.models import det, landmark_p, recog, align
from models import PeopleInfo
from django.http import JsonResponse
from server.settings import IS_IMAGE,IMAGE_SIZE
from utils.base_response import BaseResponse
from utils.file_size import get_file_size
import os
import threading
import base64
import numpy as np
import cv2
import json
import logging
import os

lock = [threading.Lock() for i in range(4)]
device_id = int(os.environ.get('DEVICE_ID',1))
logger = logging.getLogger(__name__)


def create_info(request):
    if request.method == 'POST':
        response_data = BaseResponse()
        name = request.POST.get('name', None)
        image = request.FILES.get("image", None)
        logger.info("接收信息，姓名{0},图片{1}".format(name,image))
        if not name:
            response_data.code = 400
            response_data.message = u"未获取信息的姓名，姓名为必填项，请刷新页面重试"
            logger.error("错误信息{}".format(response_data.message))
            return JsonResponse(response_data.dict)
        if not image:
            response_data.code = 400
            response_data.message = u"未获取到上传的照片，照片为必填项，请刷新页面重试"
            logger.error("错误信息{}".format(response_data.message))
            return JsonResponse(response_data.dict)

        file_name = image.name.encode('unicode-escape').decode('string_escape')
        image_name,image_suffix = file_name.rsplit(".")
        if image_suffix not in IS_IMAGE:
            response_data.code = 400
            response_data.message = u"上传的文件必须是照片，请重新上传"
            logger.error("错误信息{}".format(response_data.message))
            return JsonResponse(response_data.dict)
        try:
            image_size,image_bytes = get_file_size(image)

            if image_size > IMAGE_SIZE:
                response_data.code = 400
                response_data.message = u'证件照不能大于500kb，请重试'
                logger.error("错误信息{}".format(response_data.message))
                return JsonResponse(response_data.dict)
        except Exception as e:
            response_data.code = 500
            response_data.message = u'图片路径错误或者图片大小计算出错，请重试'
            logger.error("错误信息{}".format(response_data.message))
            return JsonResponse(response_data.dict)
       
        image_base64 = base64.b64encode(image_bytes)
        img = cv2.imdecode(np.fromstring(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        global device_id
        # 获取线程锁
        lock[device_id].acquire()
        try:
            #  获取特征值
            check_flag, feature = get_feature_out_gpu_set(img, det, landmark_p, recog,
                                                           align, device_id)
            print feature,"feature+++"
            is_create = PeopleInfo.objects.create(name=name,image=image,image_base64=image_base64,feature=feature)
            print is_create
            if is_create:
                response_data.code = 200
                response_data.message = u'信息存储成功'
                logger.info("错误信息{}".format(response_data.message))
                return JsonResponse(response_data.dict)
            else:
                response_data.code = 500
                response_data.message = u'信息存储失败'
                logger.error("错误信息{}".format(response_data.message))
                return JsonResponse(response_data.dict)
        except Exception as e:
            response_data.code = 500
            response_data.message = u"获取特征值失败，请稍后重试"
            logger.error("错误信息{}".format(response_data.message))
            return JsonResponse(response_data.dict)
        finally:
            # 释放线程锁
            lock[device_id].release()
