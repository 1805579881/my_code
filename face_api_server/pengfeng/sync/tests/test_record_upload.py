"""
匹配记录上传单元测试，生成模拟数据进行功能的验证。
"""
import json
import time
import uuid

from django.test import TestCase
from django.urls import reverse

from rest.models import Person, Record
from sync.models import Device
import base64
from io import BytesIO

import numpy as np
from PIL import Image


def get_random_base64_image_str():
    img_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
    buffer = BytesIO()
    img.save(buffer, format="png")
    img_str = base64.b64encode(buffer.getvalue())
    return img_str.decode('ascii')


class RecordUpdateTests(TestCase):

    def setUp(self):
        self.people = [
            Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str(),
                                  employee_number='1'),
            Person.objects.create(name='Tom', position='developer', image=get_random_base64_image_str(),
                                  employee_number='2'),
            Person.objects.create(name='Tony', position='product manager', image=get_random_base64_image_str(),
                                  employee_number='3')
        ]
        self.device = Device.objects.create(name='测试设备', position='正门', device_type='IN')
        self.device.members.add(*self.people)
        self.device.save()
        self.person = self.people[0]

    def test_upload_single_person_single_record_succeed(self):
        """上传单人单条匹配记录，并返回成功结果"""
        expected = {
            "error": False,
        }
        url = reverse('sync:upload-record')
        records = {
            "records": [
                {
                    'uuid': str(self.people[0].uuid),
                    'mills': [time.time()]
                }
            ]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 1)

    def test_upload_single_person_single_record_fail(self):
        """上传单个错误人员的单条匹配记录，并返回警告信息"""
        fake_uuid = str(uuid.uuid1())
        expected = {
            "error": False,
            'warning': {
                'unmatched': [fake_uuid]
            }
        }
        url = reverse('sync:upload-record')
        records = {
            "records": [
                {
                    'uuid': fake_uuid,
                    'mills': [time.time()]
                }
            ]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 0)

    def test_upload_single_person_multiple_record_succeed(self):
        """上传单人多条匹配记录，并返回成功结果"""
        expected = {
            "error": False,
        }
        url = reverse('sync:upload-record')
        records = {
            "records": [
                {
                    'uuid': str(self.people[0].uuid),
                    'mills': [time.time() for _ in range(10)]
                }
            ]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 10)

    def test_upload_single_person_multiple_record_fail(self):
        """上传单个错误人员的多条匹配记录，并返回警告信息"""
        fake_uuid = str(uuid.uuid1())
        expected = {
            "error": False,
            'warning': {
                'unmatched': [fake_uuid]
            }
        }
        url = reverse('sync:upload-record')
        records = {
            "records": [
                {
                    'uuid': fake_uuid,
                    'mills': [time.time() for _ in range(10)]
                }
            ]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 0)

    def test_upload_multiple_person_single_record_succeed(self):
        """上传多人单条匹配记录，并返回成功结果"""
        expected = {
            "error": False,
        }
        url = reverse('sync:upload-record')
        records = {
            'records': [{
                'uuid': str(person.uuid),
                'mills': [time.time()]
            } for person in self.people]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 3)

    def test_upload_multiple_person_single_record_fail(self):
        """上传多个错误人员的单条匹配记录，并返回警告信息"""
        fake_uuid_list = [str(uuid.uuid1()) for _ in range(3)]
        expected = {
            "error": False,
            'warning': {
                'unmatched': fake_uuid_list
            }
        }
        url = reverse('sync:upload-record')
        records = {
            'records': [{
                'uuid': fake_uuid,
                'mills': [time.time()]
            } for fake_uuid in fake_uuid_list]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 0)

    def test_upload_multiple_person_multiple_record_succeed(self):
        """上传多人多条匹配记录，并返回成功结果"""
        expected = {
            "error": False,
        }
        url = reverse('sync:upload-record')
        records = {
            'records': [{
                'uuid': str(person.uuid),
                'mills': [time.time() for _ in range(10)]
            } for person in self.people]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 30)

    def test_upload_multiple_person_multiple_record_fail(self):
        """上传多个错误人员的多条匹配记录，并返回警告信息"""
        fake_uuid_list = [str(uuid.uuid1()) for _ in range(3)]
        expected = {
            "error": False,
            'warning': {
                'unmatched': fake_uuid_list
            }
        }
        url = reverse('sync:upload-record')
        records = {
            'records': [{
                'uuid': fake_uuid,
                'mills': [time.time() for _ in range(10)]
            } for fake_uuid in fake_uuid_list]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 0)

    def test_upload_empty_record(self):
        """上传空白匹配记录，返回错误信息"""
        expected = {
            "error": True,
            "detail": "匹配记录为空"
        }
        url = reverse('sync:upload-record')
        records = {
            "records": [
            ]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json',
                                    **headers)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_upload_single_person_different_header(self):
        """HTTP请求头必须符合要求"""
        expected = {
            "error": True,
            'detail': 'HTTP请求头只能为application/json'
        }
        url = reverse('sync:upload-record')
        records = {
            "records": [
                {
                    'uuid': str(self.people[0].uuid),
                    'mills': [time.time()]
                }
            ]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=records, **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 0)

    def test_upload_multiple_person_different_header(self):
        """HTTP请求头必须符合要求"""
        expected = {
            "error": True,
            'detail': 'HTTP请求头只能为application/json'
        }
        url = reverse('sync:upload-record')
        records = {
            'records': [{
                'uuid': str(person.uuid),
                'mills': [time.time() for _ in range(10)]
            } for person in self.people]
        }
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data=records, **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
        self.assertEqual(Record.objects.count(), 0)
