import os, sys, django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()
import json
from django.db.models import Sum
from apps.projects.models import SituationTravaux

ca_par_mois = (
    SituationTravaux.objects
    .filter(statut__in=['payee', 'validee'])
    .values('mois', 'annee')
    .annotate(total=Sum('montant_periode_ht_dzd'))
    .order_by('annee', 'mois')
)
print('ca_par_mois:', list(ca_par_mois))

mois_labels = []
mois_data = []
MOIS = ['','Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
for entry in ca_par_mois:
    mois_labels.append(f"{MOIS[entry['mois']]} {entry['annee']}")
    mois_data.append(float(entry['total']))
print('Labels:', json.dumps(mois_labels))
print('Data:', json.dumps(mois_data))
