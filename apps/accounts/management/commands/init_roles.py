from django.core.management.base import BaseCommand
from apps.accounts.models import Role

class Command(BaseCommand):
    help = 'Initialise les rôles par défaut du système en phase avec les groupes existants'

    def handle(self, *args, **options):
        roles = [
            {'nom': 'admin', 'description': 'Administrateur complet du système'},
            {'nom': 'dg', 'description': 'Directeur Général - Accès total'},
            {'nom': 'rh', 'description': 'Responsable des Ressources Humaines'},
            {'nom': 'chef_projet', 'description': 'Chef de Projet'},
            {'nom': 'comptable', 'description': 'Comptabilité et Finance'},
            {'nom': 'achats', 'description': 'Responsable Achats'},
            {'nom': 'parc', 'description': 'Responsable Matériel et Parc'},
        ]

        for r_data in roles:
            role, created = Role.objects.get_or_create(nom=r_data['nom'], defaults={'description': r_data['description']})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Rôle '{role.nom}' créé."))
            else:
                role.description = r_data['description']
                role.save()
                self.stdout.write(f"Rôle '{role.nom}' mis à jour.")
