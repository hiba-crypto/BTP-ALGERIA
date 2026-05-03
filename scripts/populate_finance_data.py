import os
import sys
import django
import datetime
from decimal import Decimal

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.finance.models import CompteBancaire, EcritureComptable, CompteComptable
from apps.projects.models import Projet
from django.contrib.auth.models import User

def populate_finance():
    print("Injection des données financières...")

    # 1. Comptes Comptables (SCF)
    c411 = CompteComptable.objects.get_or_create(numero="411", defaults={'intitule': "Clients", 'classe': 4, 'type_compte': 'actif'})[0]
    c512 = CompteComptable.objects.get_or_create(numero="512", defaults={'intitule': "Banques", 'classe': 5, 'type_compte': 'actif'})[0]
    c631 = CompteComptable.objects.get_or_create(numero="631", defaults={'intitule': "Rémunérations du personnel", 'classe': 6, 'type_compte': 'charge'})[0]

    # 2. Comptes Bancaires
    cpa = CompteBancaire.objects.get_or_create(
        banque="CPA",
        intitule="Compte Principal CPA",
        defaults={'numero_compte': "0040012345678901", 'rib': "00400123456789012345", 'solde_dzd': 45000000}
    )[0]
    
    # 3. Écritures Comptables
    prj1 = Projet.objects.all()[0]
    admin = User.objects.get(username='admin')

    # Encaissement
    EcritureComptable.objects.get_or_create(
        reference="EC-2024-001",
        defaults={
            'date_ecriture': datetime.date.today(),
            'libelle': "Encaissement Situation n°1 - PRJ-001",
            'compte_debit': c512,
            'compte_credit': c411,
            'montant_dzd': 15000000,
            'projet': prj1,
            'statut': 'valide',
            'created_by': admin
        }
    )

    print("Données financières injectées !")

if __name__ == '__main__':
    populate_finance()
