from decimal import Decimal
from django.utils import timezone
import datetime
from django.db.models import Sum, Avg, Max, Min

def calculer_valeur_residuelle(engin):
    """
    Calcule la valeur après amortissement.
    """
    from datetime import date
    years_diff = date.today().year - engin.annee_mise_en_service
    if years_diff <= 0:
        return engin.valeur_achat_dzd
    
    depreciation = (engin.valeur_achat_dzd * (engin.taux_amortissement_annuel / 100)) * years_diff
    return max(Decimal('0'), engin.valeur_achat_dzd - depreciation)

def generer_alertes_flotte():
    """
    Liste les alertes CT, assurance et maintenance.
    """
    from .models import Engin, Maintenance
    today = timezone.now().date()
    next_month = today + datetime.timedelta(days=30)
    
    alertes = {
        'ct': Engin.objects.filter(prochain_ct_date__lte=next_month, is_active=True),
        'assurance': Engin.objects.filter(expiration_assurance__lte=next_month, is_active=True),
        'maintenance': Maintenance.objects.filter(statut='planifiee', date_entree__lte=today)
    }
    return alertes

def calculer_cout_engin_projet(engin, projet):
    """
    Calcule le coût total d'allocation pour un engin sur un projet.
    """
    from .models import AllocationEngin
    total = AllocationEngin.objects.filter(
        engin=engin, 
        projet=projet
    ).aggregate(Sum('cout_total_dzd'))['cout_total_dzd__sum'] or Decimal('0.00')
    return total

def calculer_consommation_moyenne(engin):
    """
    L/heure sur les 3 derniers mois.
    """
    from .models import BonCarburant
    three_months_ago = timezone.now().date() - datetime.timedelta(days=90)
    bons = BonCarburant.objects.filter(engin=engin, date__gte=three_months_ago)
    
    total_litres = bons.aggregate(Sum('quantite_litres'))['quantite_litres__sum'] or 0
    # On compare le premier et le dernier compteur d'heures sur la période
    if bons.count() > 1:
        max_h = bons.aggregate(Max('compteur_heures'))['compteur_heures__max']
        min_h = bons.aggregate(Min('compteur_heures'))['compteur_heures__min']
        heures = max_h - min_h
        if heures > 0:
            return Decimal(total_litres) / Decimal(heures)
    return Decimal('0.00')
