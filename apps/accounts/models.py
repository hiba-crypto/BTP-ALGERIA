from django.db import models
from django.contrib.auth.models import User, Permission

class Wilaya(models.Model):
    code = models.CharField(max_length=2, unique=True)
    nom_fr = models.CharField(max_length=100)
    nom_ar = models.CharField(max_length=100)
    
    @property
    def nom(self):
        return self.nom_fr
        
    def __str__(self):
        return f"{self.code} - {self.nom_fr}"

class Role(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.nom

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    must_change_password = models.BooleanField(default=True)
    last_password_change = models.DateTimeField(auto_now_add=True)
    two_fa_enabled = models.BooleanField(default=False)
    two_fa_secret = models.CharField(max_length=32, blank=True, null=True)
    failed_login_count = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_ua = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username
