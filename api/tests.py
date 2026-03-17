"""
SwiftSync AI — API Tests

Run with:  python3 manage.py test api
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Resource, Request


def make_user(username, password='testpass123'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_resource(donor, title='Test Resource', category='books', quantity=5):
    return Resource.objects.create(
        donor=donor,
        title=title,
        category=category,
        quantity=quantity,
        location='Test City',
        status='available'
    )


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        res = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'securepass123',
            'password2': 'securepass123',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', res.data)

    def test_register_password_mismatch(self):
        res = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'password': 'pass1234',
            'password2': 'different',
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_jwt_token(self):
        make_user('tokenuser', 'mypassword')
        res = self.client.post('/api/token/', {
            'username': 'tokenuser',
            'password': 'mypassword',
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_protected_endpoint_without_token(self):
        res = self.client.get('/api/resources/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class ResourceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.donor = make_user('donor')
        self.other = make_user('other')
        # Get JWT token for donor
        res = self.client.post('/api/token/', {'username': 'donor', 'password': 'testpass123'})
        self.token = res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_resource(self):
        res = self.client.post('/api/resources/', {
            'donor': self.donor.id,
            'title': '10 Python Books',
            'category': 'books',
            'quantity': 10,
            'location': 'Library',
            'status': 'available',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], '10 Python Books')

    def test_list_resources(self):
        make_resource(self.donor)
        make_resource(self.donor, title='Another Resource')
        res = self.client.get('/api/resources/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_single_resource(self):
        resource = make_resource(self.donor)
        res = self.client.get(f'/api/resources/{resource.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], resource.title)

    def test_update_own_resource(self):
        resource = make_resource(self.donor)
        res = self.client.patch(f'/api/resources/{resource.id}/', {'quantity': 99})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_own_resource(self):
        resource = make_resource(self.donor)
        res = self.client.delete(f'/api/resources/{resource.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_delete_others_resource(self):
        resource = make_resource(self.other)
        res = self.client.delete(f'/api/resources/{resource.id}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_category(self):
        make_resource(self.donor, category='food')
        make_resource(self.donor, category='books')
        res = self.client.get('/api/resources/?category=food')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_my_resources(self):
        make_resource(self.donor)
        make_resource(self.other)
        res = self.client.get('/api/resources/my/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for r in res.data:
            self.assertEqual(r['donor'], self.donor.id)


class RequestTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.donor = make_user('donor2')
        self.receiver = make_user('receiver')
        self.resource = make_resource(self.donor)
        # Login as receiver
        res = self.client.post('/api/token/', {'username': 'receiver', 'password': 'testpass123'})
        self.token = res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_request(self):
        res = self.client.post('/api/requests/', {
            'resource': self.resource.id,
            'receiver': self.receiver.id,
            'message': 'I need this please',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_cannot_request_own_resource(self):
        # Login as donor
        res = self.client.post('/api/token/', {'username': 'donor2', 'password': 'testpass123'})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {res.data["access"]}')
        res = self.client.post('/api/requests/', {
            'resource': self.resource.id,
            'receiver': self.donor.id,
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_request(self):
        # Create a request as receiver
        req = Request.objects.create(
            resource=self.resource, receiver=self.receiver, status='pending'
        )
        # Switch to donor
        donor_token = self.client.post('/api/token/', {'username': 'donor2', 'password': 'testpass123'}).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {donor_token}')
        res = self.client.patch(f'/api/requests/{req.id}/approve/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        req.refresh_from_db()
        self.assertEqual(req.status, 'approved')

    def test_stats_endpoint(self):
        res = self.client.get('/api/stats/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('total_resources', res.data)
        self.assertIn('resources_by_category', res.data)
