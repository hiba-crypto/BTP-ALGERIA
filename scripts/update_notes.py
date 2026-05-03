import os
import sys
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append(os.getcwd())
django.setup()

from apps.suppliers.models import Fournisseur

notes = [4.8, 4.5, 4.2, 4.9, 3.8, 4.6, 4.7]

for i, f in enumerate(Fournisseur.objects.all()):
    note = notes[i % len(notes)]
    f.note_qualite = Decimal(str(note))
    f.save()
    print(f"Mis à jour {f.raison_sociale} avec une note de {f.note_qualite}")
