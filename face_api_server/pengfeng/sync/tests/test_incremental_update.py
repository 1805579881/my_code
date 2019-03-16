"""
增量更新单元测试，生成模拟数据进行功能的验证。
"""
from django.test import TestCase
from django.urls import reverse

from rest.models import Person
from sync.models import Device, Version
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


class IncrementalUpdateTests(TestCase):

    def setUp(self):
        """
        模拟实际的操作流程进行人脸数据录入，得到一系列版本更新信息：
        1. 增加1号
        2. 增加2号
        3. 增加3号
        4. 修改1号
        5. 增加4号
        6. 修改4号
        7. 修改2号
        8. 增加5号
        9. 删除1号
        10.删除4号
        11. 删除5号
        """
        self.device = Device.objects.create(name='侧门摄像头1', position='正门', device_type='IN')

        self.people = []
        position = 'manager'

        self.people.append(
            Person.objects.create(name='person_1', position=position, image=get_random_base64_image_str()))
        self.people.append(
            Person.objects.create(name='person_2', position=position, image=get_random_base64_image_str()))

        self.people.append(
            Person.objects.create(name='person_3', position=position, image=get_random_base64_image_str()))

        self.people[0].position = 'employee'
        self.people[0].save()

        self.people.append(
            Person.objects.create(name='person_4', position=position, image=get_random_base64_image_str()))

        self.people[3].position = 'employee'
        self.people[3].save()

        self.people[1].position = 'employee'
        self.people[1].save()

        self.people.append(
            Person.objects.create(name='person_5', position=position, image=get_random_base64_image_str()))

        self.people[0].delete()
        self.people[3].delete()
        self.people[4].delete()

        self.device.members.add(self.people[1])
        self.device.save()
        content = {
            'created': set(),
            'updated': set(),
            'deleted': set()
        }
        content['updated'].add(str(self.people[1].uuid))
        Version.objects.create(content=content)

    def test_correct_version(self):
        expected = {
            "error": False,
            "is_latest": False,
            "current_version": 12,
            "clear": False,
            "created": [],
            "updated": [
                {
                    "uuid": str(self.people[1].uuid),
                    "name": self.people[1].name,
                    "position": self.people[1].position,
                    "image": self.people[1].image
                }
            ],
            "deleted": [
                str(self.people[0].uuid),
                str(self.people[2].uuid),
                str(self.people[3].uuid),
                str(self.people[4].uuid)
            ]
        }
        url = reverse('sync:get-version-difference')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.get(url, {'current_version': '2', 'format': 'json'}, **headers)
        result = response.json()
        expected_created = set([person['uuid'] for person in expected['created']])
        result_created = set([person['uuid'] for person in result['created']])
        expected_updated = set([person['uuid'] for person in expected['updated']])
        result_updated = set([person['uuid'] for person in result['updated']])
        self.assertSetEqual(expected_created, result_created)
        self.assertSetEqual(expected_updated, result_updated)
        self.assertSetEqual(set(expected['deleted']), set(result['deleted']))
        self.assertEqual(expected['error'], result['error'])
        self.assertEqual(expected['is_latest'], result['is_latest'])
        self.assertEqual(expected['current_version'], result['current_version'])
        self.assertEqual(expected['clear'], result['clear'])

    def test_larger_version(self):
        expected = {
            "error": True,
            "detail": "当前版本号大于服务器版本号"
        }
        url = reverse('sync:get-version-difference')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.get(url, {'current_version': '100', 'format': 'json'}, **headers)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_incorrect_version(self):
        expected = {
            "error": True,
            "detail": "版本号必须是一个整数"
        }
        url = reverse('sync:get-version-difference')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.get(url, {'current_version': 'Jack', 'format': 'json'}, **headers)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_is_latest(self):
        expected = {
            "error": False,
            "is_latest": True,
            "current_version": 12
        }
        url = reverse('sync:get-version-difference')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.get(url, {'current_version': '12', 'format': 'json'}, **headers)
        result = response.json()
        self.assertDictEqual(expected, result)

    def test_version_is_none(self):
        expected = {
            "error": False,
            "is_latest": False,
            "current_version": 12,
            "clear": True,
            "created": [
                {
                    "uuid": str(self.people[1].uuid),
                    "name": self.people[1].name,
                    "position": self.people[1].position,
                    "image": self.people[1].image
                }
            ],
            "updated": [],
            "deleted": [str(self.people[0].uuid),
                        str(self.people[2].uuid),
                        str(self.people[3].uuid),
                        str(self.people[4].uuid)]
        }
        url = reverse('sync:get-version-difference')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.get(url, {'format': 'json'}, **headers)
        result = response.json()
        expected_created = set([person['uuid'] for person in expected['created']])
        result_created = set([person['uuid'] for person in result['created']])
        expected_updated = set([person['uuid'] for person in expected['updated']])
        result_updated = set([person['uuid'] for person in result['updated']])
        self.assertSetEqual(expected_created, result_created)
        self.assertSetEqual(expected_updated, result_updated)
        self.assertSetEqual(set(expected['deleted']), set(result['deleted']))


class IncrementalUpdateOptionalTests(TestCase):
    def setUp(self):
        self.device = Device.objects.create(name='测试设备', position='正门', device_type='IN')

    def test_server_empty_version(self):
        expected = {
            "error": True,
            "detail": "服务器无可用版本"
        }
        url = reverse('sync:get-version-difference')
        headers = {
            'HTTP_DEVICE_ID': str(self.device.uuid)
        }
        response = self.client.get(url, {'format': 'json'}, **headers)
        result = response.json()
        self.assertDictEqual(expected, result)
