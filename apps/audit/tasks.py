from celery import shared_task
from django.core.management import call_command
import datetime
from django.core.mail import EmailMessage
from django.conf import settings
import os

@shared_task
def backup_postgresql():
    """
    Simule un backup PostgreSQL chiffré.
    """
    # En environnement réel, on utiliserait pg_dump | gpg
    print(f"[{datetime.datetime.now()}] Lancement du backup chiffré GPG...")
    return "Backup réussi."

@shared_task
def envoyer_rapport_audit_mensuel():
    """
    Génère et envoie le rapport d'audit au DG et Admin.
    """
    last_month = datetime.datetime.now().month - 1
    year = datetime.datetime.now().year
    if last_month == 0:
        last_month = 12
        year -= 1
        
    # Appeler la commande management
    call_command('generate_audit_report', month=last_month, year=year)
    
    filename = f"Rapport_Audit_{year}_{last_month:02d}.xlsx"
    filepath = os.path.join(settings.MEDIA_ROOT, 'reports', 'audit', filename)
    
    if os.path.exists(filepath):
        email = EmailMessage(
            'Rapport d\'Audit Mensuel - BTP Algeria',
            'Veuillez trouver ci-joint le rapport d\'audit pour le mois dernier.',
            settings.DEFAULT_FROM_EMAIL,
            ['admin@btpalgeria.dz', 'dg@btpalgeria.dz']
        )
        email.attach_file(filepath)
        email.send()
        return "Rapport envoyé."
    
    return "Fichier rapport non trouvé."
