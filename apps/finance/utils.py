from decimal import Decimal
from django.db.models import Sum
from apps.projects.models import RentabiliteProjet, SituationTravaux

def calculer_tva(montant_ht, taux):
    """
    Calcule la TVA et le TTC.
    """
    tva = montant_ht * (Decimal(taux) / Decimal('100.0'))
    ttc = montant_ht + tva
    return tva, ttc

def calculer_tap(ca_ht):
    """
    Calcule la TAP (Taxe sur l'Activité Professionnelle) - 2% en Algérie pour le BTP.
    """
    return ca_ht * Decimal('0.02')

def calculer_ibs(benefice_net):
    """
    Calcule l'IBS (Impôt sur le Bénéfice des Sociétés) - 26% pour BTP/Services en Algérie.
    """
    if benefice_net > 0:
        return benefice_net * Decimal('0.26')
    return Decimal('0.00')

def generer_balance_comptes(date_debut, date_fin):
    # Implementation placeholder for Balance Comptable
    return []

def generer_grand_livre(compte, date_debut, date_fin):
    # Implementation placeholder for Grand Livre
    return []

def calculer_rentabilite_projet(projet):
    """
    Met à jour l'entité RentabiliteProjet basée sur les dépenses et les revenus.
    """
    from apps.suppliers.models import BonCommande
    from apps.fleet.models import AllocationEngin
    
    rentabilite, created = RentabiliteProjet.objects.get_or_create(projet=projet)
    
    # Chiffre d'Affaire Réalisé = Somme des situations validées/payées (HT)
    ca = SituationTravaux.objects.filter(
        projet=projet, 
        statut__in=['validee', 'payee']
    ).aggregate(Sum('montant_periode_ht_dzd'))['montant_periode_ht_dzd__sum'] or Decimal('0.00')
    
    rentabilite.ca_realise_dzd = ca
    
    # Coût Matériaux = BC confirmés sur ce projet
    rentabilite.cout_materiaux_dzd = BonCommande.objects.filter(
        projet=projet,
        statut__in=['confirme', 'livre_partiel', 'livre_total']
    ).aggregate(Sum('montant_ht_dzd'))['montant_ht_dzd__sum'] or Decimal('0.00')
    
    # Coût Engins = Allocations sur ce projet
    rentabilite.cout_engins_dzd = AllocationEngin.objects.filter(
        projet=projet
    ).aggregate(Sum('cout_total_dzd'))['cout_total_dzd__sum'] or Decimal('0.00')
    
    # Coût MO (Simulé pour l'instant ou basé sur les présences si logique complexe)
    # total_charges = rentabilite.cout_mo_dzd + ...
    
    total_charges = (
        rentabilite.cout_mo_dzd + 
        rentabilite.cout_materiaux_dzd + 
        rentabilite.cout_engins_dzd + 
        rentabilite.cout_sous_traitance_dzd
    )
    
    rentabilite.marge_brute_dzd = ca - total_charges
    if ca > 0:
        rentabilite.marge_brute_pct = (rentabilite.marge_brute_dzd / ca) * Decimal('100.0')
        
    rentabilite.marge_nette_dzd = rentabilite.marge_brute_dzd - rentabilite.frais_generaux_dzd
    if ca > 0:
        rentabilite.marge_nette_pct = (rentabilite.marge_nette_dzd / ca) * Decimal('100.0')
        
    # Calcul des pénalités
    if projet.date_fin_reelle_prevue and projet.date_fin_contractuelle:
        delta = (projet.date_fin_reelle_prevue - projet.date_fin_contractuelle).days
        if delta > 0:
            rentabilite.retard_jours = delta
            rentabilite.penalites_dzd = projet.montant_marche_ttc_dzd * projet.taux_penalite_retard * Decimal(delta)
            
    rentabilite.save()
    return rentabilite
