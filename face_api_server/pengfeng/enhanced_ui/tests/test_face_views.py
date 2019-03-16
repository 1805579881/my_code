from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
import base64
from io import BytesIO
from rest.models import Person
from sync.models import Device
import numpy as np
from PIL import Image
from datetime import date
import random
from sync.models import Version
import uuid

EXAMPLE_IMAGE_PATH = 'examples/face_example.jpg'
EXAMPLE_BATCH_ZIP = 'examples/demo.zip'
EXAMPLE_NOT_ENOUGH_BATCH_ZIP = 'examples/demo_not_enough.zip'


def get_random_base64_image_str():
    img_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
    buffer = BytesIO()
    img.save(buffer, format="png")
    img_str = base64.b64encode(buffer.getvalue())
    return img_str.decode('ascii')


class FaceTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username='jack', email='12345@qq.com', password='123456')
        self.client.login(username='jack', password='123456')

    def test_index_login(self):
        url = reverse('enhanced_ui:index')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('enhanced_ui:face-list'))

    def test_index_logout(self):
        self.client.logout()
        url = reverse('enhanced_ui:index')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_list_login(self):
        url = reverse('enhanced_ui:face-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_list.html')

    def test_face_list_logout(self):
        self.client.logout()
        url = reverse('enhanced_ui:face-list')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_create_get_login(self):
        url = reverse('enhanced_ui:face-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_create.html')

    def test_face_create_get_logout(self):
        self.client.logout()
        url = reverse('enhanced_ui:face-create')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_create_post_login(self):
        url = reverse('enhanced_ui:face-create')
        data = {
            'name': '测试人员',
            'position': '经理',
            'employee_number': '12345',
            'raw_image': open(EXAMPLE_IMAGE_PATH, mode='rb'),
            'employment_date': date.today(),
            'department': '硬件部'
        }
        response = self.client.post(url, data=data)
        person = Person.objects.get(employee_number='12345')
        self.assertRedirects(response, reverse('enhanced_ui:face-update', kwargs={'pk': person.pk}))

    def test_face_create_post_logout(self):
        self.client.logout()
        url = reverse('enhanced_ui:face-create')
        data = {
            'name': '测试人员',
            'position': '经理',
            'employee_number': '12345',
            'raw_image': open(EXAMPLE_IMAGE_PATH, mode='rb'),
            'employment_date': date.today()
        }
        response = self.client.post(url, data=data)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_update_get_login(self):
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-update', kwargs={'pk': person.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_update.html')

    def test_face_update_get_logout(self):
        self.client.logout()
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-update', kwargs={'pk': person.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_update_post_login(self):
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-update', kwargs={'pk': person.pk})
        data = {
            'name': '测试人员',
            'position': '经理',
            'employee_number': '123456',
            'raw_image': open(EXAMPLE_IMAGE_PATH, mode='rb'),
            'employment_date': date.today(),
            'department': '硬件部'
        }
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('enhanced_ui:face-detail', kwargs={'pk': person.pk}))

    def test_face_update_post_logout(self):
        self.client.logout()
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-update', kwargs={'pk': person.pk})
        data = {
            'name': '测试人员',
            'position': '经理',
            'employee_number': '123456',
            'raw_image': open(EXAMPLE_IMAGE_PATH, mode='rb'),
            'employment_date': date.today()
        }
        response = self.client.post(url, data=data)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_detail_get_login(self):
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-detail', kwargs={'pk': person.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_detail.html')

    def test_face_detail_get_logout(self):
        self.client.logout()
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-detail', kwargs={'pk': person.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_delete_get_login(self):
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-delete', kwargs={'pk': person.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_delete.html')

    def test_face_delete_get_logout(self):
        self.client.logout()
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-delete', kwargs={'pk': person.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_delete_post_login(self):
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-delete', kwargs={'pk': person.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('enhanced_ui:face-list'))

    def test_face_delete_post_logout(self):
        self.client.logout()
        person = Person.objects.create(name='测试人员', position='经理', employee_number='12345',
                                       image=get_random_base64_image_str(),
                                       employment_date=date.today())
        url = reverse('enhanced_ui:face-delete', kwargs={'pk': person.pk})
        response = self.client.post(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_batch_create_get_login(self):
        url = reverse('enhanced_ui:face-batch-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_batch_create.html')

    def test_face_batch_create_get_logout(self):
        self.client.logout()
        url = reverse('enhanced_ui:face-batch-create')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_batch_create_post_login(self):
        url = reverse('enhanced_ui:face-batch-create')
        response = self.client.post(url, {'file': open(EXAMPLE_BATCH_ZIP, mode='rb')})
        self.assertRedirects(response, reverse('enhanced_ui:face-list'))
        self.assertEqual(Person.objects.count(), 4)

    def test_face_batch_create_post_logout(self):
        self.client.logout()
        url = reverse('enhanced_ui:face-batch-create')
        response = self.client.post(url, {'file': open(EXAMPLE_BATCH_ZIP, mode='rb')})
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_face_batch_create_post_not_enough_data(self):
        url = reverse('enhanced_ui:face-batch-create')
        response = self.client.post(url, {'file': open(EXAMPLE_NOT_ENOUGH_BATCH_ZIP, mode='rb')})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_batch_create.html')

    def test_face_batch_create_duplicated_person(self):
        Person.objects.create(name='Tom', position='CEO', employee_number='perfx001',
                              image=get_random_base64_image_str())
        url = reverse('enhanced_ui:face-batch-create')
        response = self.client.post(url, {'file': open(EXAMPLE_BATCH_ZIP, mode='rb')})
        self.assertRedirects(response, reverse('enhanced_ui:face-list'))
        self.assertEqual(Person.objects.count(), 4)

    def test_face_batch_create_post_invalid_file(self):
        url = reverse('enhanced_ui:face-batch-create')
        response = self.client.post(url, {'file': open(EXAMPLE_IMAGE_PATH, mode='rb')})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/face_batch_create.html')

    def test_delete_selected_people_succeed(self):
        count = random.randint(20, 50)
        pks = []
        for i in range(count):
            person = Person.objects.create(name='测试人员{}'.format(i), position='测试职位{}'.format(i),
                                           employee_number='测试工号{}'.format(i), image=get_random_base64_image_str())
            pks.append(person.pk)
        self.assertEqual(Person.objects.filter(is_deleted=False).count(), count)
        previous_version_count = Version.objects.count()
        selected_count = random.randint(1, count)
        selected_pks = random.sample(pks, selected_count)
        url = reverse('enhanced_ui:face-delete-selected')
        response = self.client.post(url, data={'pks[]': selected_pks})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Person.objects.filter(is_deleted=False).count(), count - selected_count)
        self.assertEqual(Version.objects.count(), previous_version_count + 1)

    def test_delete_selected_people_wrong_pk_format(self):
        url = reverse('enhanced_ui:face-delete-selected')
        response = self.client.post(url, data={'pks[]': [str(uuid.uuid1())]})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['error'])

    def test_set_devices_succeed(self):
        count = random.randint(20, 50)
        pks = []
        for i in range(count):
            device_type = random.choice(['IN', 'OUT'])
            device = Device.objects.create(name='测试设备{}'.format(i), position='测试位置{}'.format(i),
                                           device_type=device_type)
            pks.append(device.pk)
        person = Person.objects.create(name='测试人员', position='测试职位', employee_number='测试工号',
                                       image=get_random_base64_image_str())
        previous_version_count = Version.objects.count()
        selected_count = random.randint(1, count)
        selected_pks = random.sample(pks, selected_count)
        url = reverse('enhanced_ui:face-set-devices')
        response = self.client.post(url, data={'devices': selected_pks, 'person_pk': person.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(person.devices.count(), selected_count)
        self.assertEqual(Version.objects.count(), previous_version_count + 1)

    def test_set_devices_wrong_pk_format(self):
        url = reverse('enhanced_ui:face-set-devices')
        response = self.client.post(url, data={'devices': [], 'person_pk': str(uuid.uuid1())})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['error'])
