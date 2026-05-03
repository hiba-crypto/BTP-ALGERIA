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

from django.contrib.auth.models import User, Group
from apps.accounts.models import Wilaya, Role
from apps.employees.models import Employe, Poste
from apps.suppliers.models import Fournisseur, DomaineActivite
from apps.fleet.models import Engin, TypeEngin
from apps.projects.models import Projet, Client

def populate():
    print("Inhibition des données de démonstration...")

    # 1. Postes & Employés
    p1 = Poste.objects.get_or_create(titre="Chef de Chantier", categorie="Cadre", coefficient=400, salaire_base_min=60000, salaire_base_max=90000)[0]
    p2 = Poste.objects.get_or_create(titre="Conducteur d'Engin", categorie="Technicien", coefficient=250, salaire_base_min=45000, salaire_base_max=65000)[0]
    
    w16 = Wilaya.objects.get(code="16")
    w31 = Wilaya.objects.get(code="31")

    e1 = Employe.objects.get_or_create(
        matricule="EMP-2024-001",
        defaults={
            'nom': "MESSAOUDI", 'prenom': "Ahmed",
            'date_naissance': datetime.date(1985, 5, 20),
            'wilaya_naissance': w16,
            'type_contrat': "CDI", 'date_embauche': datetime.date(2020, 1, 1),
            'poste': p1, 'wilaya_travail': w16,
            'salaire_base_crypt': "75000",
            'mode_paiement': "virement_cpa"
        }
    )[0]

    # 2. Fournisseurs
    dom1 = DomaineActivite.objects.get_or_create(nom="Gros Oeuvre")[0]
    dom2 = DomaineActivite.objects.get_or_create(nom="Location Engins")[0]

    f1 = Fournisseur.objects.get_or_create(
        raison_sociale="COSIDER Construction",
        defaults={
            'forme_juridique': "SPA",
            'registre_commerce': "RC-123456", 'nif': "NIF-0001", 'nis': "NIS-0001", 'article_imposition': "ART-0001",
            'wilaya': w16, 'commune': "Dar El Beida", 'adresse': "Zone Industrielle",
            'telephone': "021000000", 'email': "contact@cosider.dz",
            'note_qualite': 4.5, 'statut': "actif"
        }
    )[0]
    f1.domaines.add(dom1)

    # 3. Parc Engins
    t1 = TypeEngin.objects.filter(nom="Pelle Hydraulique").first()
    if not t1:
        t1 = TypeEngin.objects.create(nom="Pelle Hydraulique", consommation_ref_lh=22.5)
    
    Engin.objects.get_or_create(
        code="ENG-CAT-001",
        defaults={
            'designation': "Caterpillar 320D",
            'type_engin': t1, 'marque': "CAT", 'modele': "320D",
            'numero_serie': "SN-987654", 'annee_fabrication': 2021, 'annee_mise_en_service': 2021,
            'valeur_achat_dzd': 18000000, 'taux_amortissement_annuel': 15.00,
            'etat': "service"
        }
    )

    # 4. Clients
    c1 = Client.objects.get_or_create(
        nom="ENPI",
        defaults={'type': "ministere", 'wilaya': w16, 'contact_nom': "Directeur ENPI", 'contact_tel': "021111111", 'contact_email': "enpi@ministere.dz"}
    )[0]
    c2 = Client.objects.get_or_create(
        nom="EMA (Entreprise Métro Alger)",
        defaults={'type': "ministere", 'wilaya': w16, 'contact_nom': "Responsable Projet", 'contact_tel': "021222222", 'contact_email': "ema@metro.dz"}
    )[0]

    # 5. Projets & Avancement
    Projet.objects.get_or_create(
        reference="PRJ-2024-001",
        defaults={
            'intitule': "Construction 500 Logements LPP - Biskra",
            'reference_marche': "M-2024-07-001",
            'client': c1,
            'type_travaux': "batiment",
            'wilaya_chantier': Wilaya.objects.get(code="07"),
            'commune_chantier': "Biskra",
            'montant_marche_ht_dzd': 850000000,
            'date_ordre_service': datetime.date(2024, 1, 15),
            'delai_execution_jours': 540,
            'avancement_pct': 35.5,
            'budget_previsionnel_dzd': 700000000,
            'statut': "en_cours"
        }
    )

    Projet.objects.get_or_create(
        reference="PRJ-2024-002",
        defaults={
            'intitule': "Extension Ligne Tramway - Oran",
            'reference_marche': "M-2023-31-045",
            'client': c2,
            'type_travaux': "tp",
            'wilaya_chantier': w31,
            'commune_chantier': "Oran",
            'montant_marche_ht_dzd': 1200000000,
            'date_ordre_service': datetime.date(2023, 11, 1),
            'delai_execution_jours': 730,
            'avancement_pct': 62.0,
            'budget_previsionnel_dzd': 1000000000,
            'statut': "en_cours"
        }
    )

    print("Données de démonstration injectées avec succès !")

if __name__ == '__main__':
    populate()
