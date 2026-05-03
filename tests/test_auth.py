from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

class AuthSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'pass123')
        self.cp_group = Group.objects.get_or_create(name='chef_projet')[0]
        self.cp_user = User.objects.create_user('cp_test', 'cp@test.com', 'pass123')
        self.cp_user.groups.add(self.cp_group)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'cp_test', 'password': 'pass123'})
        self.assertEqual(response.status_code, 302)

    def test_rbac_chef_projet_cannot_access_finance(self):
        self.client.login(username='cp_test', password='pass123')
        response = self.client.get(reverse('finance_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirected due to lack of permission

    def test_session_timeout(self):
        from django.conf import settings
        self.assertEqual(settings.SESSION_COOKIE_AGE, 1800)

    def test_password_hasher_is_secure(self):
        from django.conf import settings
        self.assertIn('django.contrib.auth.hashers.Argon2PasswordHasher', settings.PASSWORD_HASHERS)
