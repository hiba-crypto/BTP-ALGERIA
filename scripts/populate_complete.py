"""
Script complet pour peupler les données manquantes:
- Situations de Travaux (pour l'évolution CA)
- Écritures Comptables multiples
- Comptes Bancaires BEA, BDL
- Allocation d'engins dans les projets (matériaux via DemandeAchat)
"""
import os, sys, django, datetime
from decimal import Decimal

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth.models import User
from apps.projects.models import Projet, SituationTravaux, RentabiliteProjet
from apps.finance.models import CompteBancaire, EcritureComptable, CompteComptable
from apps.fleet.models import Engin, AllocationEngin
from apps.suppliers.models import DemandeAchat

admin = User.objects.get(username='admin')

# ============================================================
# 1. SITUATIONS DE TRAVAUX (pour l'évolution du CA)
# ============================================================
projets = list(Projet.objects.all())

situations_data = [
    # (projet_index, numero, mois, annee, cumul_ht, periode_ht, statut)
    (0, 1, 1, 2024, 85000000,  85000000,  'payee'),
    (0, 2, 2, 2024, 170000000, 85000000,  'payee'),
    (0, 3, 3, 2024, 255000000, 85000000,  'validee'),
    (1, 1, 3, 2024, 52700000,  52700000,  'payee'),
    (1, 2, 4, 2024, 105400000, 52700000,  'payee'),
    (1, 3, 5, 2024, 158100000, 52700000,  'validee'),
    (2, 1, 2, 2024, 187500000, 187500000, 'payee'),
]

for prj_idx, num, mois, annee, cumul, periode, statut in situations_data:
    prj = projets[prj_idx]
    if SituationTravaux.objects.filter(projet=prj, numero=num).exists():
        continue
    sit = SituationTravaux(
        projet=prj, numero=num, mois=mois, annee=annee,
        montant_cumul_ht_dzd=cumul, montant_periode_ht_dzd=periode,
        avance_demarrage_dzd=0,
        retenue_garantie_dzd=0, net_a_facturer_dzd=0,
        tva_dzd=0, net_ttc_dzd=0,
        statut=statut, created_by=admin
    )
    sit.save()  # le save() du modèle recalcule les montants
    print(f"  Situation {num} du projet {prj.reference} créée.")

# Mettre à jour l'avancement des projets
for prj in projets:
    dernier = prj.situations.order_by('-numero').first()
    if dernier and prj.montant_marche_ht_dzd > 0:
        prj.avancement_pct = (dernier.montant_cumul_ht_dzd / prj.montant_marche_ht_dzd) * 100
        prj.save()
        print(f"  Avancement {prj.reference}: {prj.avancement_pct}%")

# ============================================================
# 2. DONNÉES DE RENTABILITÉ (Répartition des charges)
# ============================================================
for prj in projets:
    rent, _ = RentabiliteProjet.objects.get_or_create(projet=prj)
    base = prj.montant_marche_ht_dzd
    rent.cout_mo_dzd           = base * Decimal('0.35')
    rent.cout_materiaux_dzd    = base * Decimal('0.28')
    rent.cout_engins_dzd       = base * Decimal('0.15')
    rent.cout_sous_traitance_dzd = base * Decimal('0.07')
    rent.frais_generaux_dzd    = base * Decimal('0.05')
    rent.save()
    print(f"  Rentabilité {prj.reference} mise à jour.")

# ============================================================
# 3. COMPTES BANCAIRES SUPPLÉMENTAIRES
# ============================================================
for banque, intitule, num, rib, solde in [
    ('BEA', 'Compte Travaux BEA', '00200045678901', '00200045678901234', 120000000),
    ('BDL', 'Compte Avances BDL', '00600012345678', '00600012345678901', 18000000),
    ('BNA', 'Compte Paie BNA',    '00100011122233', '00100011122233445', 8000000),
]:
    CompteBancaire.objects.get_or_create(
        banque=banque,
        intitule=intitule,
        defaults={'numero_compte': num, 'rib': rib, 'solde_dzd': solde}
    )
    print(f"  Compte {banque} créé.")

# ============================================================
# 4. COMPTES COMPTABLES (SCF algérien)
# ============================================================
comptes_scf = [
    ('411', 'Clients', 4, 'actif'),
    ('401', 'Fournisseurs', 4, 'passif'),
    ('512', 'Banques', 5, 'actif'),
    ('530', 'Caisse', 5, 'actif'),
    ('631', 'Rémunérations du personnel', 6, 'charge'),
    ('641', 'Sous-traitance', 6, 'charge'),
    ('226', 'Matériaux et fournitures', 6, 'charge'),
    ('706', 'Produits d\'activité principale', 7, 'produit'),
]
comptes = {}
for num, intitule, classe, typ in comptes_scf:
    c, _ = CompteComptable.objects.get_or_create(
        numero=num, defaults={'intitule': intitule, 'classe': classe, 'type_compte': typ}
    )
    comptes[num] = c
    print(f"  Compte SCF {num} - {intitule}")

# ============================================================
# 5. ÉCRITURES COMPTABLES MULTIPLES
# ============================================================
ecritures_data = [
    ('EC-2024-002', datetime.date(2024, 2, 28), 'Encaissement Situation 1 - PRJ-002', '512', '411', 62847000, 0),
    ('EC-2024-003', datetime.date(2024, 3, 31), 'Paiement Salaires Mars 2024',        '631', '512', 4200000, 1),
    ('EC-2024-004', datetime.date(2024, 4, 15), 'Paiement Fournisseur COSIDER',        '401', '512', 8500000, 0),
    ('EC-2024-005', datetime.date(2024, 4, 30), 'Encaissement Situation 2 - PRJ-001', '512', '411', 101320000, 0),
    ('EC-2024-006', datetime.date(2024, 5, 5),  'Paiement Sous-traitant Tramway',      '641', '512', 12000000, 1),
    ('EC-2024-007', datetime.date(2024, 5, 31), 'Paiement Salaires Mai 2024',          '631', '512', 4500000, 2),
    ('EC-2025-001', datetime.date(2025, 1, 15), 'Encaissement Situation 3 - PRJ-002', '512', '411', 62847000, 0),
    ('EC-2025-002', datetime.date(2025, 2, 28), 'Paiement Matériaux PRJ-003',          '226', '512', 9800000, 2),
]

for ref, date, libelle, debit_num, credit_num, montant, prj_idx in ecritures_data:
    if EcritureComptable.objects.filter(reference=ref).exists():
        continue
    prj = projets[prj_idx] if prj_idx < len(projets) else None
    EcritureComptable.objects.create(
        reference=ref, date_ecriture=date, libelle=libelle,
        compte_debit=comptes[debit_num], compte_credit=comptes[credit_num],
        montant_dzd=montant, projet=prj, statut='valide', created_by=admin
    )
    print(f"  Écriture {ref} créée.")

# ============================================================
# 6. ALLOCATIONS D'ENGINS DANS LES PROJETS
# ============================================================
engins = list(Engin.objects.all())
alloc_data = [
    # (engin_idx, projet_idx, date_debut, date_fin, heures, taux_j)
    (0, 0, datetime.date(2024, 1, 10), datetime.date(2024, 6, 30), 1200, 25000),
    (0, 1, datetime.date(2024, 3, 1),  None,                         800, 18000),
]
for eng_idx, prj_idx, debut, fin, heures, taux in alloc_data:
    if eng_idx >= len(engins) or prj_idx >= len(projets):
        continue
    engin = engins[eng_idx]
    prj = projets[prj_idx]
    alloc, created = AllocationEngin.objects.get_or_create(
        engin=engin, projet=prj,
        defaults={'date_debut': debut, 'date_fin': fin, 'heures_travaillees': heures, 'taux_journalier_dzd': taux}
    )
    if created:
        alloc.heures_travaillees = heures
        alloc.save()
        print(f"  Allocation {engin.code} -> {prj.reference} créée.")

print("\n✅ Injection complète terminée !")
