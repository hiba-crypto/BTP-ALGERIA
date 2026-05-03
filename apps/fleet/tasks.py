from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
import datetime
from .models import Engin
from django.conf import settings

@shared_task
def verifier_echeances_flotte():
    """
    Vérifie les échéances CT et Assurance et envoie un email.
    """
    today = timezone.now().date()
    next_month = today + datetime.timedelta(days=30)
    
    engins_ct = Engin.objects.filter(prochain_ct_date__lte=next_month, is_active=True)
    engins_assur = Engin.objects.filter(expiration_assurance__lte=next_month, is_active=True)
    
    if engins_ct.exists() or engins_assur.exists():
        subject = "Alerte Échéances Flotte - BTP Algeria"
        message = "Les engins suivants ont des échéances proches (moins de 30 jours) :\n\n"
        
        if engins_ct.exists():
            message += "--- Contrôle Technique ---\n"
            for e in engins_ct:
                message += f"- {e.code} ({e.designation}) : {e.prochain_ct_date}\n"
        
        if engins_assur.exists():
            message += "\n--- Assurance ---\n"
            for e in engins_assur:
                message += f"- {e.code} ({e.designation}) : {e.expiration_assurance}\n"
        
        # In real scenario, get emails of fleet managers
        recipient_list = ['responsable_parc@btpalgeria.dz', 'admin@btpalgeria.dz']
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        
        return f"Alerte envoyée pour {engins_ct.count() + engins_assur.count()} engins."
    
    return "Aucune échéance proche."
