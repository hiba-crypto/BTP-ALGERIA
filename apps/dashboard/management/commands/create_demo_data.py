from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.apps import apps
from django.utils import timezone
from decimal import Decimal
import datetime
import random

class Command(BaseCommand):
    help = 'Génère des données de démonstration ultra-complètes pour BTP Algeria'

    def handle(self, *args, **options):
        self.stdout.write("--- Début de la génération des données démo ---")
        
        # Modèles
        Employe = apps.get_model('employees', 'Employe')
        Poste = apps.get_model('employees', 'Poste')
        Wilaya = apps.get_model('accounts', 'Wilaya')
        Client = apps.get_model('projects', 'Client')
        Projet = apps.get_model('projects', 'Projet')
        SituationTravaux = apps.get_model('projects', 'SituationTravaux')
        TypeEngin = apps.get_model('fleet', 'TypeEngin')
        Engin = apps.get_model('fleet', 'Engin')
        AllocationEngin = apps.get_model('fleet', 'AllocationEngin')
        CompteComptable = apps.get_model('finance', 'CompteComptable')
        CompteBancaire = apps.get_model('finance', 'CompteBancaire')
        EcritureComptable = apps.get_model('finance', 'EcritureComptable')
        BonCommande = apps.get_model('suppliers', 'BonCommande')
        LigneBonCommande = apps.get_model('suppliers', 'LigneBonCommande')
        Fournisseur = apps.get_model('suppliers', 'Fournisseur')
        DomaineActivite = apps.get_model('suppliers', 'DomaineActivite')
        PublicQuoteRequest = apps.get_model('dashboard', 'PublicQuoteRequest')

        # 1. Wilayas de référence
        try:
            alger = Wilaya.objects.get(code='16')
            oran = Wilaya.objects.get(code='31')
            blida = Wilaya.objects.get(code='09')
        except Wilaya.DoesNotExist:
            self.stderr.write("Wilayas non trouvées. Lancez d'abord: python manage.py load_initial_data")
            return

        # 2. Domaines d'activité
        domaines_noms = ["Gros Œuvre", "Second Œuvre", "VRD", "Électricité", "Plomberie", "Matériaux de construction", "Location d'engins"]
        dom_objs = [DomaineActivite.objects.get_or_create(nom=d)[0] for d in domaines_noms]

        # 3. Fournisseurs avec Note Qualité et Historique
        fournisseurs_data = [
            ("SARL ALGERIE CIMENT", "SARL", "16", "Birkhadem", "021 55 44 33", "contact@algerieciment.dz", [0, 5], 4.5),
            ("EURL BATIMETAL DZ", "EURL", "09", "Boufarik", "025 33 22 11", "info@batimetal.dz", [0, 2], 4.8),
            ("SPA ELECTRA ALGER", "SPA", "16", "Hydra", "023 11 22 33", "sales@electra.dz", [3], 3.9),
            ("SNC HYDRAU-EST", "SNC", "25", "Constantine", "031 99 88 77", "contact@hydrauest.dz", [2, 4], 4.2),
            ("TRANS-BETON ORAN", "SARL", "31", "Es Senia", "041 22 33 44", "beton@trans-oran.dz", [0, 5], 4.6),
        ]
        
        frn_objs = []
        for rs, fj, w_code, comm, tel, mail, d_idx, note in fournisseurs_data:
            f, _ = Fournisseur.objects.get_or_create(
                raison_sociale=rs,
                defaults={
                    'forme_juridique': fj,
                    'wilaya': Wilaya.objects.get(code=w_code),
                    'commune': comm,
                    'adresse': f"Zone Industrielle, {comm}",
                    'telephone': tel,
                    'email': mail,
                    'statut': 'actif',
                    'note_qualite': Decimal(str(note)),
                    'registre_commerce': f"RC-{random.randint(100000, 999999)}",
                    'nif': f"NIF-{random.randint(10000000, 99999999)}",
                    'nis': f"NIS-{random.randint(10000000, 99999999)}",
                    'article_imposition': f"ART-{random.randint(1000, 9999)}"
                }
            )
            for idx in d_idx:
                f.domaines.add(dom_objs[idx])
            frn_objs.append(f)

        # 4. Clients
        clients_data = [
            ("OPGI d'Alger", "wilaya", alger, "Mr. Amrani", "021 66 77 88"),
            ("Ministère de l'Habitat", "ministere", alger, "Direction des Projets", "023 55 66 77"),
        ]
        client_objs = []
        for nom, typ, wil, cont, tel in clients_data:
            c, _ = Client.objects.get_or_create(
                nom=nom,
                defaults={'type': typ, 'wilaya': wil, 'contact_nom': cont, 'contact_tel': tel, 'contact_email': f"contact@demo.dz"}
            )
            client_objs.append(c)

        # 5. Employés et Postes
        p_ing, _ = Poste.objects.get_or_create(
            titre="Ingénieur Principal", 
            defaults={'salaire_base_min': 100000, 'salaire_base_max': 250000, 'coefficient': 500, 'categorie': 'Cadre'}
        )
        p_rh, _ = Poste.objects.get_or_create(
            titre="Directeur RH", 
            defaults={'salaire_base_min': 120000, 'salaire_base_max': 300000, 'coefficient': 600, 'categorie': 'Cadre_sup'}
        )
        p_comptable, _ = Poste.objects.get_or_create(
            titre="Comptable Principal", 
            defaults={'salaire_base_min': 80000, 'salaire_base_max': 150000, 'coefficient': 400, 'categorie': 'Maitrise'}
        )

        u_chef, _ = User.objects.get_or_create(username="chef_projet", defaults={'is_staff': True})
        u_rh, _ = User.objects.get_or_create(username="directeur_rh", defaults={'is_staff': True})
        u_comptable, _ = User.objects.get_or_create(username="comptable", defaults={'is_staff': True})

        base_emp_data = {
            'wilaya_travail': alger, 'commune_naissance': 'Alger', 'wilaya_naissance': alger, 
            'date_naissance': datetime.date(1980, 1, 1), 'adresse': 'Alger', 'telephone': '0550000000',
            'cni': '123456789', 'num_cnas': '456789012', 'nif_fiscal': '789012345', 'rib_bancaire': 'RIB123',
            'contact_urgence_nom': 'Urgence', 'contact_urgence_tel': '0550000000',
            'situation_familiale': 'marie', 'type_contrat': 'CDI', 'date_embauche': datetime.date(2020, 1, 1)
        }

        chef_e, _ = Employe.objects.get_or_create(
            user=u_chef, matricule='CP-001',
            defaults={**base_emp_data, 'nom': 'Mansour', 'prenom': 'Ahmed', 'poste': p_ing, 'salaire_base_crypt': "150000"}
        )
        rh_e, _ = Employe.objects.get_or_create(
            user=u_rh, matricule='RH-001',
            defaults={**base_emp_data, 'nom': 'Bennacer', 'prenom': 'Samir', 'poste': p_rh, 'salaire_base_crypt': "180000", 'cni': '987654321'}
        )
        comp_e, _ = Employe.objects.get_or_create(
            user=u_comptable, matricule='FI-001',
            defaults={**base_emp_data, 'nom': 'Khelil', 'prenom': 'Fatima', 'poste': p_comptable, 'salaire_base_crypt': "110000", 'cni': '456123789'}
        )

        # 6. Projets Réels
        projets_data = [
            ("PRJ-2024-001", "Cité 500 Logements LPL", client_objs[0], alger, 550000000.00, 480000000.00),
            ("PRJ-2024-002", "Nouveau Lycée 800 Places", client_objs[1], oran, 320000000.00, 280000000.00),
            ("PRJ-2024-003", "Hôpital 240 Lits", client_objs[0], blida, 1250000000.00, 1100000000.00),
            ("PRJ-2024-004", "Aménagement Urbain", client_objs[1], alger, 150000000.00, 120000000.00),
        ]
        
        prj_objs = []
        for ref, intit, cl, wil, m_ht, budg in projets_data:
            p, _ = Projet.objects.get_or_create(
                reference=ref,
                defaults={
                    'intitule': intit, 'client': cl, 'type_travaux': 'batiment', 'wilaya_chantier': wil,
                    'commune_chantier': "Centre", 'montant_marche_ht_dzd': Decimal(str(m_ht)),
                    'budget_previsionnel_dzd': Decimal(str(budg)), 'chef_projet': chef_e,
                    'date_ordre_service': datetime.date(2024, 1, 1), 'delai_execution_jours': 720, 'statut': 'en_cours'
                }
            )
            prj_objs.append(p)

        # 7. Achats : Demandes, Devis et Bons de Commande
        DemandeAchat = apps.get_model('suppliers', 'DemandeAchat')
        DevisComparaison = apps.get_model('suppliers', 'DevisComparaison')

        da, _ = DemandeAchat.objects.get_or_create(
            reference="DA-2024-001",
            defaults={
                'objet': 'Approvisionnement Ciment et Acier pour Fondation',
                'projet': prj_objs[0],
                'quantite': Decimal('1500.00'),
                'unite': 'Sacs/Tonnes',
                'montant_estime_dzd': Decimal('4000000.00'),
                'urgence': 'urgente',
                'justification': 'Rupture de stock imminente sur chantier principal',
                'demandeur': u_chef,
                'statut': 'approuvee',
                'approuve_par': u_rh,
                'date_approbation': timezone.now()
            }
        )

        DevisComparaison.objects.get_or_create(
            demande=da,
            fournisseur=frn_objs[0],
            defaults={
                'montant_ht_dzd': Decimal('3800000.00'),
                'taux_tva': Decimal('19.00'),
                'delai_livraison_jours': 5,
                'conditions_paiement': '30 jours fin de mois',
                'est_retenu': True,
                'note': 'Meilleur rapport qualité/prix'
            }
        )

        for i, p in enumerate(prj_objs):
            bc, _ = BonCommande.objects.get_or_create(
                reference=f"BC-2024-{i+1:03d}",
                defaults={
                    'fournisseur': frn_objs[i % len(frn_objs)],
                    'projet': p,
                    'date_commande': timezone.now().date() - datetime.timedelta(days=30),
                    'date_livraison_prevue': timezone.now().date() - datetime.timedelta(days=15),
                    'statut': 'confirme',
                    'montant_ht_dzd': Decimal('2500000.00'),
                    'created_by': u_chef
                }
            )
            LigneBonCommande.objects.get_or_create(
                bon_commande=bc, designation="Ciment CPJ 42.5", 
                defaults={'quantite': 1000, 'unite': "Sacs", 'prix_unitaire_ht_dzd': 1200, 'montant_ht_dzd': 1200000}
            )
            LigneBonCommande.objects.get_or_create(
                bon_commande=bc, designation="Acier HA 12", 
                defaults={'quantite': 10, 'unite': "Tonnes", 'prix_unitaire_ht_dzd': 130000, 'montant_ht_dzd': 1300000}
            )

        # 8. Matériel et Allocations
        t_pelle, _ = TypeEngin.objects.get_or_create(nom="Pelle Hydraulique", defaults={'consommation_ref_lh': 15.0})
        t_camion, _ = TypeEngin.objects.get_or_create(nom="Camion Benne", defaults={'consommation_ref_lh': 20.0})
        
        engin1, _ = Engin.objects.get_or_create(
            numero_serie="SN-CAT-001",
            defaults={
                'designation': 'Pelle CAT 336', 'type_engin': t_pelle, 'marque': 'Caterpillar', 'modele': '336GC',
                'annee_fabrication': 2022, 'annee_mise_en_service': 2022, 'valeur_achat_dzd': 25000000.0,
                'taux_amortissement_annuel': 10.0, 'etat': 'en_service', 'code': 'ENG-001'
            }
        )
        engin2, _ = Engin.objects.get_or_create(
            numero_serie="SN-MB-002",
            defaults={
                'designation': 'Mercedes Arocs', 'type_engin': t_camion, 'marque': 'Mercedes', 'modele': 'Arocs',
                'annee_fabrication': 2023, 'annee_mise_en_service': 2023, 'valeur_achat_dzd': 18000000.0,
                'taux_amortissement_annuel': 15.0, 'etat': 'en_service', 'code': 'ENG-002'
            }
        )
        
        RentabiliteProjet = apps.get_model('projects', 'RentabiliteProjet')
        for i, p in enumerate(prj_objs):
            # Allocate engins
            AllocationEngin.objects.get_or_create(
                engin=engin1 if i % 2 == 0 else engin2, projet=p,
                defaults={
                    'date_debut': datetime.date(2024, 2, 1) + datetime.timedelta(days=i*10), 
                    'taux_journalier_dzd': 45000.0 if i % 2 == 0 else 30000.0, 
                    'heures_travaillees': 120 + i*50,
                    'cout_total_dzd': (45000.0 if i % 2 == 0 else 30000.0) * (30 + i*5)
                }
            )
            # Update Rentabilite to add Sous Traitance and MO
            rent, _ = RentabiliteProjet.objects.get_or_create(projet=p)
            rent.cout_sous_traitance_dzd = Decimal(str(5000000 + i * 2000000))
            rent.cout_mo_dzd = Decimal(str(3000000 + i * 1000000))
            rent.frais_generaux_dzd = Decimal(str(1000000 + i * 500000))
            rent.save()

        # 9. Situations et Avancement
        for i, p in enumerate(prj_objs):
            m_periode = p.montant_marche_ht_dzd * Decimal(str(0.15 + i*0.05))
            SituationTravaux.objects.get_or_create(
                projet=p, numero=1,
                defaults={
                    'mois': (i % 12) + 1, 'annee': 2024, 'montant_cumul_ht_dzd': m_periode, 'montant_periode_ht_dzd': m_periode,
                    'statut': 'payee', 'date_soumission': datetime.date(2024, (i % 12) + 1, 5), 'date_paiement': datetime.date(2024, (i % 12) + 1, 10)
                }
            )
            p.avancement_pct = float(15.0 + i*5.0)
            p.save()

        # 10. Finances (Comptes et Écritures)
        cb, _ = CompteBancaire.objects.get_or_create(banque='CPA', numero_compte='001001', defaults={'intitule': 'CPA Main', 'solde_dzd': 150000000.0})
        try:
            c_achat = CompteComptable.objects.get(numero='601000')
            c_fourn = CompteComptable.objects.get(numero='400000')
            EcritureComptable.objects.get_or_create(
                reference="EC-2024-001", 
                defaults={
                    'date_ecriture': timezone.now().date(), 'libelle': "Achat Matériaux Démo",
                    'compte_debit': c_achat, 'compte_credit': c_fourn, 'montant_dzd': Decimal('2500000.00'), 
                    'projet': prj_objs[0], 'statut': 'valide'
                }
            )
        except CompteComptable.DoesNotExist:
            pass

        # 10. Demandes Externes
        PublicQuoteRequest.objects.get_or_create(
            email="contact@client-externe.dz",
            defaults={
                'nom_complet': "Kamel Zergui",
                'sujet': "Demande de Devis - Route Nationale",
                'message': "Bonjour, nous souhaiterions obtenir un devis pour la réfection d'une route de 5km à Bouira. Merci."
            }
        )

        self.stdout.write(self.style.SUCCESS("--- Génération des données démo terminée avec succès ---"))
