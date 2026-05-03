import os
import django
import sys

# Ajouter le répertoire racine au sys.path
sys.path.append('c:/Users/hp/Desktop/BTP')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth.models import User, Group
from apps.accounts.models import Role, UserProfile

roles_groups = {
    'admin': 'admin',
    'dg_benali': 'dg',
    'rh_kamel': 'rh',
    'comptable_amina': 'comptable'
}

password = 'Admin@2025!'

print("--- Initialisation des comptes de test demandés ---")

for username, rg in roles_groups.items():
    u, created = User.objects.get_or_create(username=username, defaults={'is_staff': True, 'email': f'{username}@btp.dz'})
    u.set_password(password)
    u.save()
    
    # Create/Get Role
    role, _ = Role.objects.get_or_create(nom=rg, defaults={'description': f'Rôle {rg}'})
    
    # Update Profile
    profile, _ = UserProfile.objects.get_or_create(user=u)
    profile.role = role
    profile.save()
    
    # Sync with Group
    group, _ = Group.objects.get_or_create(name=rg)
    u.groups.clear()
    u.groups.add(group)
    
    status = "créé" if created else "mis à jour"
    print(f"Compte '{username}' {status} (Rôle: {rg}, Mot de passe: {password})")

print("--- Opération terminée ---")
