from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import File
from .utils import generate_encrypted_url

User = get_user_model()

class FileSharingAPITestCase(APITestCase):

    def setUp(self):
        self.client_user = User.objects.create_user(username='client', password='password', email='client@example.com', role='client')
        self.ops_user = User.objects.create_user(username='ops', password='password', email='ops@example.com', role='ops')
        self.client = APIClient()

    def test_signup(self):
        url = reverse('signup')
        data = {
            "username": "newclient",
            "password": "password",
            "email": "newclient@example.com",
            "role": "client",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_verify_email(self):
        # Assuming you have an endpoint to generate the verification link
        # and another to verify it
        verification_url = reverse('verify_email', kwargs={'encrypted_url': 'encrypted_url_string'})
        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        url = reverse('login')
        data = {
            "username": "client",
            "password": "password"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_upload_file(self):
        self.client.login(username='ops', password='password')
        url = reverse('upload_file')
        with open('path/to/file.docx', 'rb') as file:
            data = {
                'file': file
            }
            response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_files(self):
        self.client.login(username='client', password='password')
        url = reverse('list_files')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_file(self):
        self.client.login(username='client', password='password')
        file = File.objects.create(name='testfile.docx', file='path/to/file.docx')
        encrypted_url = generate_encrypted_url(file.id, self.client_user.id)
        url = reverse('encrypted_download_file', kwargs={'encrypted_url': encrypted_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
