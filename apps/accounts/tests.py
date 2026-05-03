from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

class SecurityTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'pass123')
        self.rh_group = Group.objects.create(name='responsable_rh')
        self.rh_user = User.objects.create_user('rh_test', 'rh@test.com', 'pass123')
        self.rh_user.groups.add(self.rh_group)
        
        self.tech_group = Group.objects.create(name='technicien')
        self.tech_user = User.objects.create_user('tech_test', 'tech@test.com', 'pass123')
        self.tech_user.groups.add(self.tech_group)

    def test_rh_access_to_employees(self):
        """RH should access employee list, Technician should be blocked."""
        # Test RH
        self.client.login(username='rh_test', password='pass123')
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        # Test Technician
        self.client.login(username='tech_test', password='pass123')
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 403) # Forbidden
        self.client.logout()

    def test_anonymous_redirect(self):
        """Anonymous users should be redirected to login."""
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
