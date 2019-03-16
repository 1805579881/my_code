"""
REST API单元测试，按照GET,POST,DELETE的顺序编写，Record只有GET，POST和DELETE有效，无法调用PUT和PATCH。
"""
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from rest.models import Person, Record
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


class RecordTests(APITestCase):
    def setUp(self):
        self.person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str())

    def test_get_record(self):
        """使用主键pk调用GET方法查询某条匹配记录，并验证返回的记录信息"""
        record = Record.objects.create(target=self.person, created=timezone.now())
        url = reverse('record-detail', kwargs={'pk': record.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], record.pk)
        self.assertEqual(response.data['target'], record.target.pk)

    def test_post_record(self):
        """调用POST方法创建匹配记录，并验证返回的记录信息"""
        url = reverse('record-list')
        data = {
            'target': self.person.id,
            'created': timezone.now()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 1)
        self.assertEqual(Record.objects.get().target, self.person)

    def test_post_record_bad_date(self):
        """调用POST方法输入错误的日期信息，验证返回的错误码"""
        url = reverse('record-list')
        data = {
            'target': self.person.id,
            'created': '0'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_bulk_post_record(self):
        """调用POST方法批量创建匹配记录，并验证返回的记录的数量"""
        url = reverse('record-list')
        data = [
            {
                'target': self.person.id,
                'created': timezone.now()
            },
            {
                'target': self.person.id,
                'created': timezone.now()
            },
            {
                'target': self.person.id,
                'created': timezone.now()
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)

    def test_delete_record(self):
        """调用DELETE方法删除匹配记录，并验证是否删除成功"""
        record = Record.objects.create(target=self.person, created=timezone.now())
        url = reverse('record-detail', kwargs={'pk': record.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Record.objects.count(), 0)

    def test_put_record_error(self):
        """无法使用PUT方法更新匹配记录，返回错误码"""
        tom = Person.objects.create(name='Tom', position='developer', image=get_random_base64_image_str())
        url = reverse('record-detail', kwargs={'pk': self.person.pk})
        data = {
            'target': tom.pk,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

    def test_patch_record_error(self):
        """无法使用PATCH方法更新匹配记录，返回错误码"""
        tom = Person.objects.create(name='Tom', position='developer', image=get_random_base64_image_str())
        url = reverse('record-detail', kwargs={'pk': self.person.pk})
        data = {
            'target': tom.pk,
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)
