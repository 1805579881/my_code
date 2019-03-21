# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from base64 import b64decode, b64encode
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import time
import math
import os
from xcmp import xcmp as xcmp_fun
from random import randint
from datetime import datetime
from face_veri_pose_cd import get_score_gpu_set, get_score, get_pose, get_pose_batch_gpu_set, get_feature_out_gpu_set
import os
import models
import threading

# Create your views here.
lock = [threading.Lock() for i in range(4)]
device_id = int(os.environ.get('DEVICE_ID'))

def load_db(idx):
    ret = []
    with open("/home/rentingting/project/face_verification/face_api_demo_cd/features/perf_part_list.txt", "r") as fo:
        for line in fo.readlines():
            [filename, id] = line.split()
            ret.append((filename, id))
    return ret


global_db = load_db("/home/rentingting/project/face_verification/face_api_demo_cd/features/perf_part_list.txt")


#global_db=[]

def create_dir(prefix, score):
    dirname = prefix + '_' + datetime.now().strftime("%Y%m%d_%H%M%S_%f_") + str(randint(100, 999)) + '_' + str(
        int(100 * score))
    # print dirname
    directory = os.path.join('.', dirname)
    # print directory
    if not os.path.exists(directory):
        os.makedirs(directory)
    return dirname


def create_result_xml(cxxh, score, success=True):
    root = ET.Element("DATA", {"CODE": "0010"})
    if cxxh:
        record = ET.SubElement(root, "RECORD", {"CXXH": cxxh})
    else:
        record = ET.SubElement(root, "RECORD")
    if success:
        result = ET.SubElement(record, "RESULT", {"COUNTER": "1"})
        rxxsd = ET.SubElement(result, "RXXSD")
        rxxsd.text = str(score)
    else:
        result = ET.SubElement(record, "RESULT", {"COUNTER": "0"})
    return ET.tostring(root, encoding="utf8")


def create_result_xml_live(cxxh, success, check_flag, shot, frame):
    root = ET.Element("DATA", {"CODE": "0010"})
    if cxxh:
        record = ET.SubElement(root, "RECORD", {"CXXH": cxxh})
    else:
        record = ET.SubElement(root, "RECORD")
    if success:
        result = ET.SubElement(record, "RESULT", {"COUNTER": "1",
                                                  "CHECK_FLAG": str(check_flag),
                                                  "SHOT": str(shot)
                                                  })
        rxxsd = ET.SubElement(result, "RXXSD")
        rxxsd.text = str(shot)
        ret, img = cv2.imencode(".jpg", frame)
        if ret:
            xml_frame = ET.SubElement(result, "BEST_FRAME")
            xml_frame.text = b64encode(img)
    else:
        result = ET.SubElement(record, "RESULT", {"COUNTER": "0"})
    return ET.tostring(root, encoding="utf8")


def load_image(idx):
    filename, id = global_db[idx]
    with open(filename) as img:
        return (b64encode(img.read()), id)


def  create_result_xml_xcmp(cxxh, success, check_flag, idx_score):
    root = ET.Element("DATA", {"CODE": "0010"})
    if cxxh:
        record = ET.SubElement(root, "RECORD", {"CXXH": cxxh})
    else:
        record = ET.SubElement(root, "RECORD")
    if success:
        result = ET.SubElement(record, "RESULT", {"COUNTER": "1",
                                                  "CHECK_FLAG": str(check_flag)
                                                  })
        for idx, score in idx_score:
            image, id = load_image(idx)
            rxxsd = ET.SubElement(result, "RXXSD", {"SCORE": str(score),
                                                    "ID": str(id)})
            rxxsd.text = image
    else:
        result = ET.SubElement(record, "RESULT", {"COUNTER": "0"})
    return ET.tostring(root, encoding="utf8")


@csrf_exempt
def index(request):
    cxxh = None
    score = 0
    success = False
    if request.method == "POST":
        data = []
        img0_str = None
        img1_str = None
        root = ET.fromstring(request.body)
        for cond in root.iter('CONDITION'):
            cxxh = cond.attrib['CXXH']
            break
        # print cxxh
        for xp1 in root.iter('XP1'):
            data.append(xp1.text)
        if len(data) > 1:
            # log raw data
            # f = open('post_data_0.log', 'w')
            # f.write(data[0])
            # f.close()
            # f = open('post_data_1.log', 'w')
            # f.write(data[1])
            # f.close()
            img0_str = b64decode(data[0])
            img1_str = b64decode(data[1])
            success = True
            t0 = time.time()
            img0 = cv2.imdecode(np.fromstring(img0_str, np.uint8), cv2.IMREAD_COLOR)
            t1 = time.time()
            img1 = cv2.imdecode(np.fromstring(img1_str, np.uint8), cv2.IMREAD_COLOR)
            t2 = time.time()
            # print models.det
            t3 = time.time()
            print >> sys.stderr, 'Decoding image 1 for %.2fms, and image 2 for %.2fms' % (
                1000.0 * (t1 - t0), 1000.0 * (t2 - t1))
            print >> sys.stderr, 'Scoring for %.1fms' % (1000.0 * (t3 - t2),)
            # dirname = create_dir('pair', score)
            # cv2.imwrite(os.path.join(dirname, '0.jpg'), img0)
            # cv2.imwrite(os.path.join(dirname, '1.jpg'), img1)
            global device_id;
            lock[device_id].acquire();
            try:
                t3 = time.time()
                print >> sys.stderr, 'start to analyze for thread %s on card %d' % (
                    threading.current_thread().getName(), device_id)
                score = get_score_gpu_set(img0, img1, models.det, models.landmark_p, models.recog, models.align,
                                          device_id);
                t4 = time.time()
                print >> sys.stderr, 'analyze ending for thread %s, %.2fms on card %d' % (
                    threading.current_thread().getName(), 1000.0 * (t4 - t3), device_id)
            finally:
                lock[device_id].release();

    # cv2.imwrite('data.jpg', img0)
    # img_file = open('data.jpg', 'wb')
    # img_file.write(img0)
    return HttpResponse(create_result_xml(cxxh, score, success), content_type='text/xml')


def read_frames(cap):
    frames = [];
    while (True):
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
        else:
            break
    cap.release()
    return frames


@csrf_exempt
def pose(request):
    cxxh = None
    pose = 4
    success = False
    check_flag = -1;
    shot = False
    frames = []
    front_idx = 0
    if request.method == 'POST':
        data = []
        img0_str = None
        root = ET.fromstring(request.body)
        pose = 1
        for cond in root.iter('CONDITION'):
            cxxh = cond.attrib['CXXH']
            pose = int(cond.attrib['POSE'])
            break
        # print cxxh
        for xp1 in root.iter('XP1'):
            img0_str = b64decode(xp1.text)
            filename = 'post_data_%s.mp4' % (threading.current_thread().getName(),)
            f = open(filename, 'w')
            f.write(img0_str)
            f.close()
            t0 = time.time()
            cap = cv2.VideoCapture(filename);
            frames = read_frames(cap)
            print >> sys.stderr, "length of frames = %d" % (len(frames),)
            global device_id
            lock[device_id].acquire();
            try:
                print >> sys.stderr, 'start to analyze pose for thread %s on card %d' % (
                    threading.current_thread().getName(), device_id)
                t1 = time.time()
                check_flag, shot, front_idx = get_pose_batch_gpu_set(frames, models.det, models.landmark_p, models.pose,
                                                                     pose, device_id)
                t2 = time.time()
                print >> sys.stderr, 'analyze pose for thread %s, %.2fms on card %d' % (
                    threading.current_thread().getName(), 1000.0 * (t2 - t1), device_id)
            finally:
                lock[device_id].release();
            # print >>sys.stderr, result, pose, ang
            success = check_flag == 1
            print 'Decoding image for %.2fms' % (1000.0 * (t1 - t0),)
            print >> sys.stderr, 'Get pose for %.1fms' % (1000.0 * (t2 - t1),)
            # dirname = create_dir('pose', pose)
            print >> sys.stderr, "success=", success, ",check_flag=", check_flag, ",shot=", shot, ",front_idx=", front_idx
            # cv2.imwrite(os.path.join(dirname, '0.jpg'), frames[front_idx])
            break
    # cv2.imwrite('data.jpg', img0)
    # img_file = open('data.jpg', 'wb')
    # img_file.write(img0)
    return HttpResponse(create_result_xml_live(cxxh, success, check_flag, shot, frames[front_idx]),
                        content_type='text/xml')


@csrf_exempt
def xcmp(request):
    cxxh = None
    success = False
    check_flag = -1;
    idx_score = []
    if request.method == 'POST':
        data = []
        img_str = None
        root = ET.fromstring(request.body)
        for cond in root.iter('CONDITION'):
            cxxh = cond.attrib['CXXH']
            break
        # print cxxh
        for xp1 in root.iter('XP1'):
            data.append(xp1.text)
        if len(data) > 0:
            img0_str = b64decode(data[0])
            # threading.current_thread().getName() 获取当前线程的方法
            filename = 'post_data_%s.jpg' % (threading.current_thread().getName(),)
            f = open(filename, 'w')
            f.write(img0_str)
            f.close()
            # 读取图片数据转成图片格式
            img = cv2.imdecode(np.fromstring(img0_str, np.uint8), cv2.IMREAD_COLOR)
            t0 = time.time()
            global device_id
            lock[device_id].acquire();
            try:
                print >> sys.stderr, 'start to extract feature for thread %s on card %d' % (
                    threading.current_thread().getName(), device_id)
                t1 = time.time()
                # feature 是一个多维的数组，就是一个面部的特征值
                check_flag, feature = get_feature_out_gpu_set(img, models.det, models.landmark_p, models.recog,
                                                              models.align, device_id)
                t2 = time.time()
                print >> sys.stderr, 'end to extract feature for thread %s, %.2fms on card %d' % (
                    threading.current_thread().getName(), 1000.0 * (t2 - t1), device_id)
            finally:
                lock[device_id].release();
            t3 = time.time();
            print >> sys.stderr, "feature shape ", feature.shape, " type:", feature.dtype

            # idx_score 匹配到的分数 ， xcmp_fun 进行数据的比对
            idx_score = xcmp_fun(np.reshape(feature, (512,)),
                                 "/home/rentingting/project/face_verification/face_api_demo_cd/features/perf_part_feature.bin".encode(
                                     "utf-8"), threshold=0.01, top=10)
            # 公式进行映射 分数0-1
            idx_score_remap = [(idx, 1.0 / (1 + math.exp(-11.945 * score + 4.97))) for idx, score in idx_score]

            print >> sys.stderr, 'Xcompare spent  for %.1fms: idx_score=%s' % (1000.0 * (t3 - t2), idx_score)
            success = check_flag == 1
            print 'Decoding image for %.2fms' % (1000.0 * (t1 - t0),)
            # if len(idx_score) > 0:
            #    dirname = create_dir('xcmp', idx_score[0][0])
            print >> sys.stderr, "success=", success, ",check_flag=", check_flag, ",idx_score=", [
                (global_db[idx], score) for idx, score in idx_score_remap]
        # cv2.imwrite(os.path.join(dirname, '0.jpg'), img)

    return HttpResponse(create_result_xml_xcmp(cxxh, success, check_flag, idx_score_remap), content_type='text/xml')
