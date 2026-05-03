from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedTextField

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAIL', 'Login Fail'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('EXPORT', 'Export'),
        ('PRINT', 'Print'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('PAYMENT', 'Payment'),
        ('SALARY_VIEW', 'Salary View'),
        ('PERMISSION_CHANGE', 'Permission Change'),
        ('SETTINGS_CHANGE', 'Settings Change'),
        ('BACKUP', 'Backup'),
    )

    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    )

    RISK_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    username_snapshot = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    module = models.CharField(max_length=50)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=500)
    old_value = EncryptedTextField(null=True)
    new_value = EncryptedTextField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='low')

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("Les logs d'audit sont immuables")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Suppression des logs interdite")
