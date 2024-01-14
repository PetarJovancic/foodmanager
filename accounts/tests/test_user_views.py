from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch


class CreateUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'cope',
            'email': 'aron@locallogic.co',
            'password': 'string'
        }

    @patch('accounts.views.PyHunter')
    @patch('accounts.views.CreateUserView.lookup_email')
    def test_create_user_success(self, mock_lookup_email, mock_pyhunter):
        """
        Test creating user.
        """
        mock_pyhunter.return_value.email_verifier.return_value = \
            {'status': 'valid'}
        mock_lookup_email.return_value = {'person': {
                                                'name': {
                                                    'givenName': 'Aron',
                                                    'familyName': 'Smith'
                                                    }
                                                }}
        response = self.client.post('/api/accounts/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
                    get_user_model().objects.filter(username='cope').exists())


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='cope',
            email='aron@locallogic.co',
            password='string'
        )
        self.login_data = {
            'username': 'cope',
            'password': 'string'
        }

    def test_login_success(self):
        """
        Test login with valid creditentials.
        """
        response = self.client.post('/api/accounts/login/', self.login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """
        Test login with invalid creditentials.
        """
        self.login_data['password'] = 'wrongpassword'
        response = self.client.post('/api/accounts/login/', self.login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
