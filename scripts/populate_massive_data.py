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
from apps.accounts.models import Wilaya, Role, UserProfile
from apps.employees.models import Employe, Poste
from apps.suppliers.models import Fournisseur, DomaineActivite, DemandeAchat
from apps.fleet.models import Engin, TypeEngin, AllocationEngin
from apps.projects.models import Projet, Client, SituationTravaux

def populate():
    print("Injection de données massives pour le Master...")

    # 0. Groupes & Rôles
    groups = ['dg', 'rh', 'comptable', 'chef_projet', 'technicien']
    for gname in groups:
        Group.objects.get_or_create(name=gname)

    # 1. Utilisateurs
    def create_user(username, group_name):
        user, created = User.objects.get_or_create(username=username, defaults={'email': f"{username}@btp.dz"})
        if created:
            user.set_password('admin123')
            user.save()
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = Role.objects.get_or_create(nom=group_name.upper())[0]
            profile.save()
        return user

    create_user('directeur', 'dg')
    create_user('rh_manager', 'rh')
    create_user('comptable1', 'comptable')
    create_user('ingenieur_chef', 'chef_projet')

    # 2. Wilayas (assurer Alger et Oran)
    w16 = Wilaya.objects.get(code="16")
    w31 = Wilaya.objects.get(code="31")
    w07 = Wilaya.objects.get(code="07")

    # 3. Employés par rôle
    p_chef = Poste.objects.get_or_create(titre="Chef de Projet", defaults={'categorie': "Cadre", 'coefficient': 500, 'salaire_base_min': 80000, 'salaire_base_max': 150000})[0]
    p_tech = Poste.objects.get_or_create(titre="Maçon Qualifié", defaults={'categorie': "Ouvrier", 'coefficient': 150, 'salaire_base_min': 35000, 'salaire_base_max': 60000})[0]

    chef1 = Employe.objects.get_or_create(
        matricule="EMP-001", defaults={
            'nom': "BENABDERRAHMANE", 'prenom': "Yacine", 'poste': p_chef, 'wilaya_naissance': w16, 'wilaya_travail': w16, 'date_embauche': datetime.date(2015, 6, 1), 'salaire_base_crypt': "120000", 'date_naissance': datetime.date(1980, 1, 1)
        }
    )[0]

    # 4. Clients & Projets
    c_prive = Client.objects.get_or_create(nom="Promotion Immobilière EL BORDJ", defaults={'type': "prive", 'wilaya': w31, 'contact_nom': "Mr Brahimi", 'contact_tel': "041000000", 'contact_email': "contact@elbordj.dz"})[0]

    prj3 = Projet.objects.get_or_create(
        reference="PRJ-2024-003",
        defaults={
            'intitule': "Réalisation d'une Tour de Bureau 15 étages",
            'reference_marche': "M-2024-31-999",
            'client': c_prive,
            'type_travaux': "batiment",
            'wilaya_chantier': w31,
            'commune_chantier': "Bir El Djir",
            'montant_marche_ht_dzd': 1500000000,
            'date_ordre_service': datetime.date(2024, 2, 1),
            'delai_execution_jours': 900,
            'avancement_pct': 12.5,
            'budget_previsionnel_dzd': 1200000000,
            'chef_projet': chef1,
            'statut': "en_cours"
        }
    )[0]

    # 5. Fournisseurs & Matériaux
    dom_acier = DomaineActivite.objects.get_or_create(nom="Acier et Ferraillage")[0]
    f_acier = Fournisseur.objects.get_or_create(
        raison_sociale="TOSYALI Algerie",
        defaults={'forme_juridique': "SPA", 'registre_commerce': "RC-TOSY-001", 'nif': "NIF-TOSY-001", 'wilaya': w31, 'email': "sales@tosyali.dz", 'note_qualite': 4.8, 'statut': "actif"}
    )[0]
    f_acier.domaines.add(dom_acier)

    # Création d'une demande d'achat pour "Matériaux"
    DemandeAchat.objects.get_or_create(
        objet="Acier HA 12 pour Projet PRJ-003",
        defaults={
            'projet': prj3, 'quantite': 50, 'unite': "Tonnes", 'montant_estime_dzd': 12000000, 'urgence': "normale", 'demandeur': User.objects.get(username="admin"), 'statut': "transformee"
        }
    )

    # 6. Engins & Allocations
    t_camion = TypeEngin.objects.get_or_create(nom="Camion Benne 20T", defaults={'consommation_ref_lh': 18.0})[0]
    engin1 = Engin.objects.get_or_create(
        code="ENG-TRK-001",
        defaults={'designation': "Renault Kerax", 'type_engin': t_camion, 'marque': "Renault", 'modele': "Kerax", 'numero_serie': "SN-RK-111", 'annee_fabrication': 2022, 'annee_mise_en_service': 2022, 'valeur_achat_dzd': 25000000, 'taux_amortissement_annuel': 10, 'etat': "en_service"}
    )[0]

    AllocationEngin.objects.get_or_create(
        engin=engin1, projet=prj3,
        defaults={'date_debut': datetime.date(2024, 2, 10), 'taux_journalier_dzd': 15000}
    )

    # 7. Rentabilité (pour les graphiques)
    from apps.projects.models import RentabiliteProjet
    for prj in Projet.objects.all():
        rent, _ = RentabiliteProjet.objects.get_or_create(projet=prj)
        rent.cout_mo_dzd = prj.montant_marche_ht_dzd * Decimal('0.35')
        rent.cout_materiaux_dzd = prj.montant_marche_ht_dzd * Decimal('0.40')
        rent.cout_engins_dzd = prj.montant_marche_ht_dzd * Decimal('0.15')
        rent.cout_sous_traitance_dzd = prj.montant_marche_ht_dzd * Decimal('0.05')
        rent.save()

    print("Injection massive terminée !")

if __name__ == '__main__':
    populate()
