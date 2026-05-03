from django.test import TestCase
from apps.audit.models import AuditLog
from django.contrib.auth.models import User

class AuditSecurityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('audit_tester', 'audit@test.com', 'pass123')
        self.log = AuditLog.objects.create(
            user=self.user,
            username_snapshot='audit_tester',
            action='CREATE',
            module='employees',
            object_repr='Employe Test',
            status='success'
        )

    def test_audit_log_immutable(self):
        # Should raise error on update
        with self.assertRaises(PermissionError):
            self.log.action = 'UPDATE'
            self.log.save()

    def test_audit_log_cannot_be_deleted(self):
        # Should raise error on delete
        with self.assertRaises(PermissionError):
            self.log.delete()
