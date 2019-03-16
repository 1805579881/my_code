"""
REST API单元测试，按照GET,POST,DELETE的顺序编写，Device只有GET有效。
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from sync.models import Device


class DeviceTests(APITestCase):
    def setUp(self):
        self.device = Device.objects.create(name='测试设备', position='正门', device_type='IN')

    def test_get_device(self):
        url = reverse('device-detail', kwargs={'uuid': self.device.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], self.device.pk)
        self.assertEqual(response.data['uuid'], str(self.device.uuid))
        self.assertEqual(response.data['name'], self.device.name)
        self.assertEqual(response.data['position'], self.device.position)
        self.assertEqual(response.data['device_type'], self.device.device_type)
