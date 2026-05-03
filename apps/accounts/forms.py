from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Role
import re
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}))

class TwoFactorForm(forms.Form):
    code = forms.CharField(
        max_length=6, 
        min_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': '123456', 'autofocus': True}),
        help_text="Entrez le code à 6 chiffres généré par votre application."
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 12:
            raise ValidationError("Le mot de passe doit contenir au moins 12 caractères.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        if not re.search(r'\d', password):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        return password

class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        required=True, 
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rôle"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            from .models import UserProfile
            from django.contrib.auth.models import Group
            profile, created = UserProfile.objects.get_or_create(user=user)
            role = self.cleaned_data['role']
            profile.role = role
            profile.save()
            
            # Sync with Groups for legacy support
            group, _ = Group.objects.get_or_create(name=role.nom)
            user.groups.clear()
            user.groups.add(group)
            
        return user

class UserUpdateForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        required=True, 
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rôle"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile') and self.instance.profile.role:
            self.fields['role'].initial = self.instance.profile.role

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            from .models import UserProfile
            from django.contrib.auth.models import Group
            profile, created = UserProfile.objects.get_or_create(user=user)
            role = self.cleaned_data['role']
            profile.role = role
            profile.save()
            
            # Sync with Groups for legacy support
            group, _ = Group.objects.get_or_create(name=role.nom)
            user.groups.clear()
            user.groups.add(group)
            
        return user

class RoleAssignForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label=None)
