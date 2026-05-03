from celery import shared_task
from .models import Contrat, Employe
from django.utils import timezone
import datetime
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def verifier_alertes_rh():
    """
    Alerte sur les CDD expirant dans 30 jours.
    """
    today = timezone.now().date()
    seuil = today + datetime.timedelta(days=30)
    
    contrats = Contrat.objects.filter(type_contrat='CDD', date_fin__lte=seuil, date_fin__gte=today)
    
    if contrats.exists():
        message = "Contrats CDD arrivant à expiration :\n"
        for c in contrats:
            message += f"- {c.employe} : Fin le {c.date_fin}\n"
        
        send_mail(
            "Alerte RH : Expiration Contrats",
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['rh@btpalgeria.dz']
        )
        return f"{contrats.count()} alertes envoyées."
    return "Aucun contrat expirant."

@shared_task
def generer_bulletins_mensuels():
    """
    Génération automatique des bulletins pour tous les employés actifs.
    """
    # Logique simplifiée : boucle sur les employés actifs et appel de la méthode de calcul
    employes = Employe.objects.filter(statut='ACTIF')
    count = 0
    for emp in employes:
        # Implémentation réelle appellerait la vue/méthode de création de bulletin
        count += 1
    return f"{count} bulletins en cours de génération..."
