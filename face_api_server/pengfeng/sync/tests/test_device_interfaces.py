"""
设备注册与更新接口单元测试
"""
import json
import uuid

from django.test import TestCase
from django.urls import reverse

from sync.models import Device


class DeviceInterfaceTests(TestCase):
    def setUp(self):
        self.device = Device.objects.create(uuid=str(uuid.uuid1()), name='test_device', device_type='IN')

    def test_create_device(self):
        """新增设备，返回成功状态码并验证设备信息"""
        new_uuid = str(uuid.uuid1())
        expected = {
            "error": False,
        }
        url = reverse('sync:create-or-update-device')
        records = {
            'device_info': {
                'uuid': new_uuid,
                'name': '测试设备',
                'position': '后门',
                'device_type': 'IN'
            }
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        device = Device.objects.get(uuid=new_uuid)
        self.assertDictEqual(expected, result)
        self.assertEqual(device.name, '测试设备')
        self.assertEqual(device.position, '后门')
        self.assertEqual(device.device_type, 'IN')
        self.assertEqual(device.ip, '127.0.0.1')

    def test_create_device_error_device_type(self):
        """设备类型只能为IN或者OUT"""
        expected = {
            "error": True,
            'detail': '设备类型错误，不能为UNKNOWN'
        }
        url = reverse('sync:create-or-update-device')
        records = {
            'device_info': {
                'uuid': str(uuid.uuid1()),
                'name': '测试设备',
                'position': '正门',
                'device_type': 'UNKNOWN'
            }
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_create_device_not_enough_data(self):
        """上传的数据必须符合要求"""
        expected = {
            "error": True,
            "detail": "设备信息不全"
        }
        url = reverse('sync:create-or-update-device')
        data = {
            'device_info': {
                'uuid': str(uuid.uuid1()),
                'name': '测试设备',
                'position': '后门'
            }
        }
        response = self.client.post(url, data=json.dumps(data, ensure_ascii=False), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_create_device_different_header(self):
        """HTTP请求头必须符合要求"""
        expected = {
            "error": True,
            "detail": "HTTP请求头只能为application/json"
        }
        url = reverse('sync:create-or-update-device')
        data = {
            'device_info': {
                'uuid': str(uuid.uuid1()),
                'name': '测试设备',
                'position': '后门',
                'device_type': 'IN'
            }
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_update_device(self):
        """更新设备，返回成功状态码并验证设备信息"""
        expected = {
            "error": False,
        }
        url = reverse('sync:create-or-update-device')
        records = {
            'device_info': {
                'uuid': self.device.uuid,
                'name': '测试设备',
                'position': '正门',
                'device_type': 'OUT'
            }
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        device = Device.objects.get(uuid=self.device.uuid)
        self.assertDictEqual(expected, result)
        self.assertEqual(device.name, '测试设备')
        self.assertEqual(device.position, '正门')
        self.assertEqual(device.device_type, 'OUT')
        self.assertEqual(device.ip, '127.0.0.1')

    def test_update_device_error_device_type(self):
        """设备类型只能为IN或者OUT"""
        expected = {
            "error": True,
            'detail': '设备类型错误，不能为UNKNOWN'
        }
        url = reverse('sync:create-or-update-device')
        records = {
            'device_info': {
                'uuid': str(self.device.uuid),
                'name': '测试设备',
                'position': '正门',
                'device_type': 'UNKNOWN'
            }
        }
        response = self.client.post(url, data=json.dumps(records, ensure_ascii=False), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_device_interface_empty_data(self):
        """测试空白数据"""
        expected = {
            "error": True,
            "detail": "设备信息为空"
        }
        url = reverse('sync:create-or-update-device')
        response = self.client.post(url, data={}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_update_device_not_enough_data(self):
        """上传的数据必须符合要求"""
        expected = {
            "error": True,
            "detail": "设备信息不全"
        }
        url = reverse('sync:create-or-update-device')
        data = {
            'device_info': {
                'uuid': str(self.device.uuid),
                'name': '测试设备',
                'position': '后门'
            }
        }
        response = self.client.post(url, data=json.dumps(data, ensure_ascii=False), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_update_device_different_header(self):
        """HTTP请求头必须符合要求"""
        expected = {
            "error": True,
            "detail": "HTTP请求头只能为application/json"
        }
        url = reverse('sync:create-or-update-device')
        data = {
            'device_info': {
                'uuid': str(self.device.uuid),
                'name': '测试设备',
                'position': '后门',
                'device_type': 'IN'
            }
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)
