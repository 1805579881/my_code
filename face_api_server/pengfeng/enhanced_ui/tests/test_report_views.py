from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
import base64
from io import BytesIO
from rest.models import Person, Record
import numpy as np
from PIL import Image
from django.utils import timezone
import uuid


def get_random_base64_image_str():
    img_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
    buffer = BytesIO()
    img.save(buffer, format="png")
    img_str = base64.b64encode(buffer.getvalue())
    return img_str.decode('ascii')


class ReportTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username='jack', email='12345@qq.com', password='123456')
        self.client.login(username='jack', password='123456')
        self.person = Person.objects.create(name='Jack', position='manager', image=get_random_base64_image_str())
        self.absent_person = Person.objects.create(name='Tom', position='manager', image=get_random_base64_image_str())
        self.record = Record.objects.create(target=self.person, created=timezone.now())

    def test_report_get_login(self):
        url = reverse('enhanced_ui:report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/report.html')

    def test_report_get_by_date(self):
        url = reverse('enhanced_ui:report-date', kwargs={'date': timezone.now().strftime('%Y-%m-%d')})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.templates[0].name, 'enhanced_ui/report.html')

    def test_report_get_logout(self):
        self.client.logout()
        url = reverse('enhanced_ui:report')
        response = self.client.get(url)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('admin:login'), url))

    def test_get_personal_records_succeed(self):
        url = reverse('enhanced_ui:personal-records')
        response = self.client.get(url, data={
            'pk': self.person.pk,
            'date': timezone.now().strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertFalse(result['error'])

    def test_get_personal_records_wrong_pk_format(self):
        url = reverse('enhanced_ui:personal-records')
        response = self.client.get(url, data={
            'pk': str(uuid.uuid1()),
            'date': timezone.now().strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertTrue(result['error'])

    def test_get_personal_records_wrong_pk(self):
        url = reverse('enhanced_ui:personal-records')
        response = self.client.get(url, data={
            'pk': '100',
            'date': timezone.now().strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertTrue(result['error'])

    def test_get_personal_records_wrong_http_method(self):
        url = reverse('enhanced_ui:personal-records')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_export_excel(self):
        url = reverse('enhanced_ui:export-records')
        response = self.client.get(url, data={
            'date': timezone.now().strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
