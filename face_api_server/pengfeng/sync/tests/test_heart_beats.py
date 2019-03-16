"""
终端监控（心跳保持）接口单元测试
"""
import json
import uuid

from django.test import TestCase
from django.urls import reverse

from sync.models import Device


class HeartBeatsTests(TestCase):
    def setUp(self):
        self.device = Device.objects.create(uuid=str(uuid.uuid1()), name='test_device', device_type='IN',
                                            ip='127.0.0.1')

    def test_heart_beat_succeed(self):
        """发送心跳请求，并返回成功状态码"""
        expected = {
            "error": False,
        }
        url = reverse('sync:heart-beats')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_heart_beat_error_device(self):
        """设备必须在服务器列表中"""
        expected = {
            "error": True,
            'detail': '设备信息无效，找不到设备'
        }
        url = reverse('sync:heart-beats')
        headers = {
            'HTTP_DEVICE_ID': str(uuid.uuid1())
        }
        response = self.client.post(url, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_heart_beat_not_enough_data(self):
        """必须包含设备UUID"""
        expected = {
            "error": True,
            "detail": "请求头部不包含设备UUID"
        }
        url = reverse('sync:heart-beats')
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_heart_beat_different_header(self):
        """HTTP请求头必须符合要求"""
        expected = {
            "error": True,
            "detail": "HTTP请求头只能为application/json"
        }
        url = reverse('sync:heart-beats')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertDictEqual(expected, result)
