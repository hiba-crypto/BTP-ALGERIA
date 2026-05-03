from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Charge toutes les données initiales (Wilayas, SCF, Rôles)'

    def handle(self, *args, **options):
        self.stdout.write("--- Chargement des Wilayas ---")
        call_command('loaddata', 'apps/employees/fixtures/wilayas.json')
        
        self.stdout.write("--- Chargement du Plan Comptable SCF ---")
        call_command('loaddata', 'apps/finance/fixtures/plan_comptable_scf.json')
        
        self.stdout.write("--- Chargement des Rôles et Groupes ---")
        call_command('loaddata', 'apps/accounts/fixtures/initial_roles.json')
        
        # Création de l'admin par défaut
        if not User.objects.filter(username='admin').exists():
            self.stdout.write("--- Création du superutilisateur 'admin' ---")
            User.objects.create_superuser('admin', 'admin@btpalgeria.dz', 'admin123')
            admin_user = User.objects.get(username='admin')
            admin_group = Group.objects.get(name='admin_systeme')
            admin_user.groups.add(admin_group)
            
        self.stdout.write(self.style.SUCCESS('Données initiales chargées avec succès.'))
