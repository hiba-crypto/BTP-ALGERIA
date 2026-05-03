import os, sys, django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.projects.models import Projet, SituationTravaux, RentabiliteProjet
from apps.finance.models import EcritureComptable, CompteBancaire
from apps.fleet.models import AllocationEngin
from apps.suppliers.models import Fournisseur

print('=== VERIFICATION DES DONNEES ===')
print(f'Projets: {Projet.objects.count()}')
print(f'Situations de Travaux: {SituationTravaux.objects.count()}')
print(f'  Payees: {SituationTravaux.objects.filter(statut="payee").count()}')
print(f'Ecritures Comptables: {EcritureComptable.objects.count()}')
print(f'Comptes Bancaires: {CompteBancaire.objects.count()}')
print(f'Allocations Engins: {AllocationEngin.objects.count()}')
print(f'Fournisseurs: {Fournisseur.objects.count()}')

print()
print('=== RENTABILITE (GRAPHIQUE REPARTITION) ===')
r = RentabiliteProjet.objects.first()
if r:
    print(f'  MO: {r.cout_mo_dzd}')
    print(f'  Materiaux: {r.cout_materiaux_dzd}')
    print(f'  Engins: {r.cout_engins_dzd}')
    print(f'  ST: {r.cout_sous_traitance_dzd}')
    print(f'  FG: {r.frais_generaux_dzd}')

print()
print('=== AVANCEMENT PROJETS ===')
for p in Projet.objects.all():
    print(f'  {p.reference}: {p.avancement_pct}%')

print()
print('=== FOURNISSEURS (NOTES) ===')
for f in Fournisseur.objects.order_by('-note_qualite')[:5]:
    print(f'  {f.raison_sociale}: {f.note_qualite}/5')
