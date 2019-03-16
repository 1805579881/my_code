"""
REST API单元测试，按照GET,POST,PUT,PATCH,DELETE的顺序编写。
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rest.models import Person
import base64
from io import BytesIO

import numpy as np
from PIL import Image
from datetime import date


def get_random_base64_image_str():
    img_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
    buffer = BytesIO()
    img.save(buffer, format="png")
    img_str = base64.b64encode(buffer.getvalue())
    return img_str.decode('ascii')


class PersonTests(APITestCase):

    def test_get_person(self):
        """使用主键pk调用GET方法查询某个人员，并验证返回的人员信息"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str(),
                                       employee_number='1')
        url = reverse('person-detail', kwargs={'pk': person.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], person.pk)
        self.assertEqual(response.data['name'], person.name)
        self.assertEqual(response.data['position'], person.position)
        self.assertEqual(response.data['image'], person.image)
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '1')

    def test_post_person(self):
        """调用POST方法创建人员，并验证返回的人员信息"""
        url = reverse('person-list')
        data = {
            'name': 'Jack',
            'position': 'manager',
            'image': get_random_base64_image_str(),
            'employee_number': '1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['name'], 'Jack')
        self.assertEqual(response.data['position'], 'manager')
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '1')

    def test_post_person_bad_date(self):
        """调用POST方法输入错误的日期信息，验证返回的错误码"""
        url = reverse('person-list')
        data = {
            'name': 'Jack',
            'position': 'manager',
            'image': get_random_base64_image_str(),
            'employment_date': '1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_bulk_post_person(self):
        """调用POST方法批量创建人员，并验证返回的人员信息"""
        url = reverse('person-list')
        data = [
            {
                'name': 'Jack',
                'position': 'manager',
                'image': get_random_base64_image_str(),
                'employee_number': '1'
            },
            {
                'name': 'Tom',
                'position': 'developer',
                'image': get_random_base64_image_str(),
                'employee_number': '2'
            },
            {
                'name': 'Tony',
                'position': 'ceo',
                'image': get_random_base64_image_str(),
                'employee_number': '3'
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        jack = response.data[0]
        self.assertEqual(jack['name'], 'Jack')
        self.assertEqual(jack['position'], 'manager')
        self.assertEqual(jack['is_active'], True)
        self.assertEqual(jack['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(jack['employee_number'], '1')

        tom = response.data[1]
        self.assertEqual(tom['name'], 'Tom')
        self.assertEqual(tom['position'], 'developer')
        self.assertEqual(tom['is_active'], True)
        self.assertEqual(tom['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(tom['employee_number'], '2')

        tony = response.data[2]
        self.assertEqual(tony['name'], 'Tony')
        self.assertEqual(tony['position'], 'ceo')
        self.assertEqual(tony['is_active'], True)
        self.assertEqual(tony['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(tony['employee_number'], '3')

    def test_put_person(self):
        """调用PUT方法更新人员，并验证返回的人员信息（PUT方法必须填写所有字段）"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str(),
                                       employee_number='1')
        url = reverse('person-detail', kwargs={'pk': person.pk})
        data = {
            'name': 'Tom',
            'position': 'employer',
            'employee_number': '2'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], person.pk)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['position'], data['position'])
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '2')

    def test_patch_person(self):
        """调用PATCH方法更新人员，并验证返回的人员信息（PATCH方法可以填写部分字段）"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str(),
                                       employee_number='1')
        url = reverse('person-detail', kwargs={'pk': person.pk})
        data = {
            'position': 'employer'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], person.pk)
        self.assertEqual(response.data['position'], data['position'])
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '1')

    def test_delete_person(self):
        """调用DELETE方法删除人员，并验证是否删除成功（软删除）"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str())
        url = reverse('person-detail', kwargs={'pk': person.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        person = Person.objects.get(pk=person.pk)
        self.assertEqual(person.is_deleted, True)

    def test_delete_all_person(self):
        """调用DELETE方法批量删除人员，并验证是否删除成功（软删除）"""
        jack = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str())
        tom = Person.objects.create(name='Tom', position='manager', image=get_random_base64_image_str())
        url = reverse('person-list')
        response = self.client.delete(url, format='json')
        jack = Person.objects.get(pk=jack.pk)
        tom = Person.objects.get(pk=tom.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertEqual(jack.is_deleted, True)
        self.assertEqual(tom.is_deleted, True)

    def test_get_custom_person(self):
        """使用uuid调用GET方法查询某个人员，并验证返回的人员信息（安卓终端调用的接口）"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str(),
                                       employee_number='1')
        url = reverse('custom_person-detail', kwargs={'uuid': person.uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], person.pk)
        self.assertEqual(response.data['uuid'], str(person.uuid))
        self.assertEqual(response.data['name'], person.name)
        self.assertEqual(response.data['position'], person.position)
        self.assertEqual(response.data['image'], person.image)
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '1')

    def test_post_custom_person(self):
        """调用POST方法创建人员，并验证返回的人员信息（安卓终端调用的接口）"""
        url = reverse('custom_person-list')
        data = {
            'name': 'Jack',
            'position': 'manager',
            'image': get_random_base64_image_str(),
            'employee_number': '1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['name'], 'Jack')
        self.assertEqual(response.data['position'], 'manager')
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '1')

    def test_post_custom_person_bad_date(self):
        """调用POST方法输入错误的日期信息，验证返回的错误码（安卓终端调用的接口）"""
        url = reverse('custom_person-list')
        data = {
            'name': 'Jack',
            'position': 'manager',
            'image': get_random_base64_image_str(),
            'employment_date': '0',
            'employee_number': '1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_bulk_post_custom_person(self):
        """调用POST方法批量创建人员，并验证返回的人员信息（安卓终端调用的接口）"""
        url = reverse('custom_person-list')
        data = [
            {
                'name': 'Jack',
                'position': 'manager',
                'image': get_random_base64_image_str(),
                'employee_number': '1'
            },
            {
                'name': 'Tom',
                'position': 'developer',
                'image': get_random_base64_image_str(),
                'employee_number': '2'
            },
            {
                'name': 'Tony',
                'position': 'ceo',
                'image': get_random_base64_image_str(),
                'employee_number': '3'
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        jack = response.data[0]
        self.assertEqual(jack['name'], 'Jack')
        self.assertEqual(jack['position'], 'manager')
        self.assertEqual(jack['is_active'], True)
        self.assertEqual(jack['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(jack['employee_number'], '1')

        tom = response.data[1]
        self.assertEqual(tom['name'], 'Tom')
        self.assertEqual(tom['position'], 'developer')
        self.assertEqual(tom['is_active'], True)
        self.assertEqual(tom['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(tom['employee_number'], '2')

        tony = response.data[2]
        self.assertEqual(tony['name'], 'Tony')
        self.assertEqual(tony['position'], 'ceo')
        self.assertEqual(tony['is_active'], True)
        self.assertEqual(tony['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(tony['employee_number'], '3')

    def test_put_custom_person(self):
        """调用PUT方法更新人员，并验证返回的人员信息（安卓终端调用的接口，PUT方法必须填写所有字段）"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str(),
                                       employee_number='1')
        url = reverse('custom_person-detail', kwargs={'uuid': person.uuid})
        data = {
            'name': 'Tom',
            'position': 'employer',
            'employee_number': '2'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], person.pk)
        self.assertEqual(response.data['uuid'], str(person.uuid))
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['position'], data['position'])
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '2')

    def test_patch_custom_person(self):
        """调用PATCH方法更新人员，并验证返回的人员信息（安卓终端调用的接口，PATCH方法可以填写部分字段）"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str(),
                                       employee_number='1')
        url = reverse('custom_person-detail', kwargs={'uuid': person.uuid})
        data = {
            'position': 'employer'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['pk'], person.pk)
        self.assertEqual(response.data['uuid'], str(person.uuid))
        self.assertEqual(response.data['position'], data['position'])
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(response.data['employment_date'], date.today().strftime('%Y-%m-%d'))
        self.assertEqual(response.data['employee_number'], '1')

    def test_delete_custom_person(self):
        """调用DELETE方法删除人员，并验证是否删除成功（安卓终端调用的接口，软删除，且返回值自定义为200）"""
        person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str())
        url = reverse('custom_person-detail', kwargs={'uuid': person.uuid})
        response = self.client.delete(url, format='json')
        person = Person.objects.get(pk=person.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json(), {})
        self.assertEqual(person.is_deleted, True)

    def test_delete_all_custom_person(self):
        """调用DELETE方法批量删除人员，并验证是否删除成功（安卓终端调用的接口，软删除）"""
        jack = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str())
        tom = Person.objects.create(name='Tom', position='manager', image=get_random_base64_image_str())
        url = reverse('custom_person-list')
        response = self.client.delete(url, format='json')
        jack = Person.objects.get(pk=jack.pk)
        tom = Person.objects.get(pk=tom.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertEqual(jack.is_deleted, True)
        self.assertEqual(tom.is_deleted, True)
