import pytest
from django.urls import reverse
from http import HTTPStatus
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.test import TestCase

@pytest.mark.django_db
class TestUserEndpoints:
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def test_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='1234567890'
        )
        return user

    @pytest.fixture
    def authenticated_client(self, api_client, test_user):
        refresh = RefreshToken.for_user(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return api_client

    def test_create_user(self, authenticated_client):
        url = reverse('user-list')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '0987654321'
        }
        
        response = authenticated_client.post(url, data)
        assert response.status_code == HTTPStatus.CREATED
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_list_users(self, authenticated_client, test_user):
        url = reverse('user-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == HTTPStatus.OK
        assert len(response.data['data']) >= 1

    def test_update_user(self, authenticated_client, test_user):
        url = reverse('user-detail', kwargs={'id': test_user.id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = authenticated_client.put(url, data)
        assert response.status_code == HTTPStatus.OK
        test_user.refresh_from_db()
        assert test_user.first_name == 'Updated'
        assert test_user.last_name == 'Name'

    def test_login(self, api_client, test_user):
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == HTTPStatus.OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data

    def test_unauthorized_access(self, api_client):
        url = reverse('user-list')
        response = api_client.get(url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_create_user_invalid_data(self, authenticated_client):
        url = reverse('user-list')
        data = {
            'email': 'invalid_email',
            'password': 'short',
        }
        
        response = authenticated_client.post(url, data)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_update_user_not_found(self, authenticated_client):
        url = reverse('user-detail', kwargs={'id': 99999})
        data = {
            'first_name': 'Updated'
        }
        
        response = authenticated_client.put(url, data)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_login_invalid_credentials(self, api_client):
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_create_user_duplicate_email(self, authenticated_client, test_user):
        url = reverse('user-list')
        data = {
            'email': 'test@example.com',  # Este email ya existe
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890'
        }
        
        response = authenticated_client.post(url, data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        
    def test_export_users_csv(self, authenticated_client, test_user):
        url = reverse('user-export-csv')
        response = authenticated_client.get(url)
        
        assert response.status_code == HTTPStatus.OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment; filename="users.csv"' in response['Content-Disposition']
        
        # Verificar contenido del CSV
        content = response.content.decode('utf-8')
        assert 'id,email,first_name,last_name,phone,date_joined' in content
        assert test_user.email in content