from decimal import Decimal
import datetime
from django.utils import timezone
from .models import BulletinPaie

def calculer_prime_anciennete(employe):
    """
    1% par année d'ancienneté, max 25%
    """
    if not employe.date_embauche:
        return Decimal('0')
    
    annees = (datetime.date.today() - employe.date_embauche).days // 365
    pct = min(annees, 25)
    return employe.salaire_base * Decimal(pct) / Decimal('100')

def calculer_irg(salaire_imposable, nb_enfants=0):
    """
    Barème IRG Algérie (simplifié 2022)
    """
    si = salaire_imposable
    irg = Decimal('0')
    
    if si <= 30000:
        return Decimal('0')
        
    if si <= 120000:
        irg = (si - 30000) * Decimal('0.20')
    elif si <= 360000:
        irg = (120000 - 30000) * Decimal('0.20') + (si - 120000) * Decimal('0.30')
    else:
        irg = (120000 - 30000) * Decimal('0.20') + (360000 - 120000) * Decimal('0.30') + (si - 360000) * Decimal('0.35')
        
    # Abattements (simplifié)
    if si > 30000 and si <= 35000:
        abattement = (137.5 * si) - Decimal('4125') # formule specifique
        irg = irg - abattement
    else:
        # Abattement standard 40% (min 1000, max 1500)
        abattement = irg * Decimal('0.40')
        if abattement < 1000: abattement = Decimal('1000')
        if abattement > 1500: abattement = Decimal('1500')
        irg = irg - abattement
        
    if irg < 0: irg = Decimal('0')
    
    # Abattement enfants
    irg = irg - (Decimal(nb_enfants) * Decimal('300'))
    if irg < 0: irg = Decimal('0')
    
    return irg

def calculer_bulletin(employe, mois, annee):
    """
    Calcule les éléments du bulletin.
    """
    salaire_base = employe.salaire_base
    prime_anciennete = calculer_prime_anciennete(employe)
    
    salaire_brut = salaire_base + prime_anciennete # + autres
    cnas = salaire_brut * Decimal('0.09')
    
    salaire_imposable = salaire_brut - cnas
    irg = calculer_irg(salaire_imposable, employe.nb_enfants)
    
    # Cotisation CACOBATPH (3% spécifique BTP)
    cacobatph = salaire_brut * Decimal('0.03')
    
    salaire_net = salaire_imposable - irg - cacobatph
    
    return {
        'salaire_base': salaire_base,
        'prime_anciennete': prime_anciennete,
        'salaire_brut': salaire_brut,
        'cnas': cnas,
        'irg': irg,
        'cacobatph': cacobatph,
        'salaire_net': salaire_net
    }

def generer_pdf_bulletin(bulletin):
    """
    Génère un PDF via ReportLab.
    """
    import os
    from django.conf import settings
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    
    filename = f"bulletin_{bulletin.employe.matricule}_{bulletin.mois}_{bulletin.annee}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'employees', 'bulletins', str(bulletin.annee), filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # En-tête
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height - 2*cm, "BTP ALGERIA SPA")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2.0, height - 4*cm, f"BULLETIN DE PAIE - {bulletin.mois}/{bulletin.annee}")
    
    # Employé
    c.drawString(2*cm, height - 6*cm, f"Matricule: {bulletin.employe.matricule}")
    c.drawString(2*cm, height - 6.5*cm, f"Nom & Prénom: {bulletin.employe.nom} {bulletin.employe.prenom}")
    c.drawString(2*cm, height - 7*cm, f"Fonction: {bulletin.employe.poste.titre}")
    
    # Montants
    c.drawString(2*cm, height - 10*cm, f"Salaire de Base: {bulletin.salaire_base} DZD")
    c.drawString(2*cm, height - 10.5*cm, f"Prime Ancienneté: {bulletin.prime_anciennete} DZD")
    c.drawString(2*cm, height - 11*cm, f"Salaire Brut: {bulletin.salaire_brut} DZD")
    c.drawString(2*cm, height - 12*cm, f"Retenue CNAS (9%): -{bulletin.cnas_salariale} DZD")
    c.drawString(2*cm, height - 12.5*cm, f"Retenue CACOBATPH (3%): -{bulletin.cacobatph_salariale} DZD")
    c.drawString(2*cm, height - 13*cm, f"Retenue IRG: -{bulletin.irg} DZD")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height - 15*cm, f"NET A PAYER: {bulletin.salaire_net} DZD")
    
    c.save()
    return f"employees/bulletins/{bulletin.annee}/{filename}"
