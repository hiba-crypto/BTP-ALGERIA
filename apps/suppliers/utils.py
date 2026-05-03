from django.utils import timezone
import datetime
from decimal import Decimal
from django.db.models import Max, Avg
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

def generer_reference(prefix, model_class):
    """
    Génère une référence unique type FRN-0001 ou DA-2026-0001
    """
    year = timezone.now().year
    
    if prefix == 'FRN':
        pattern = f"{prefix}-"
        last_obj = model_class.objects.filter(code__startswith=pattern).order_by('-code').first()
        last_ref = last_obj.code if last_obj else None
    else:
        pattern = f"{prefix}-{year}-"
        last_obj = model_class.objects.filter(reference__startswith=pattern).order_by('-reference').first()
        last_ref = last_obj.reference if last_obj else None

    if last_ref:
        try:
            last_number = int(last_ref.split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            new_number = 1
    else:
        new_number = 1

    return f"{pattern}{new_number:04d}"

def calculer_note_fournisseur(fournisseur):
    """
    Calcule la note qualité basée sur les réceptions (conformité) et délais.
    """
    from .models import BonReception
    receptions = BonReception.objects.filter(bon_commande__fournisseur=fournisseur)
    
    if not receptions.exists():
        return fournisseur.note_qualite
    
    # Calcul simple : % de conformité
    total = receptions.count()
    conformes = receptions.filter(statut='conforme').count()
    note_conformite = (conformes / total) * 5.0
    
    # On peut aussi moyenner avec la note existante
    nouvelle_note = (fournisseur.note_qualite + Decimal(str(note_conformite))) / 2
    return nouvelle_note.quantize(Decimal('0.01'))

def verifier_seuil_approbation(montant_dzd):
    """
    Retourne le rôle requis pour l'approbation d'un BC selon les seuils du décret 15-247.
    - < 500k : Achat simple (Responsable Achats)
    - 500k - 8M : Marché gré à gré (Directeur Général)
    - > 8M : Procédure formelle (Directeur Général + Audit)
    """
    if montant_dzd <= 500000:
        return "Responsable Achats"
    elif montant_dzd <= 8000000:
        return "DG"
    else:
        return "DG_AUDIT"

def generer_pdf_bon_commande(bc):
    """
    Génère un fichier PDF officiel pour le Bon de Commande avec le cachet.
    """
    from django.conf import settings
    
    filename = f"{bc.reference}.pdf"
    folder_path = os.path.join(settings.MEDIA_ROOT, 'achats', 'bons_commande')
    filepath = os.path.join(folder_path, filename)
    os.makedirs(folder_path, exist_ok=True)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # --- En-tête ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "BTP ALGERIA SPA")
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, height - 2.5*cm, "Adresse : Zone Industrielle, Alger")
    c.drawString(2*cm, height - 3*cm, "NIF : 000016000000000 | RC : 16/00-0000000B00")
    
    # --- Titre ---
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2.0, height - 5*cm, f"BON DE COMMANDE N° {bc.reference}")
    
    # --- Informations ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 7*cm, f"Date : {bc.date_commande.strftime('%d/%m/%Y')}")
    c.drawString(2*cm, height - 7.6*cm, f"Projet : {bc.projet.nom if bc.projet else 'N/A'}")
    
    # Bloc Fournisseur (à droite)
    c.rect(11*cm, height - 8.5*cm, 8*cm, 2.5*cm)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(11.5*cm, height - 6.6*cm, "FOURNISSEUR :")
    c.setFont("Helvetica", 11)
    c.drawString(11.5*cm, height - 7.2*cm, bc.fournisseur.raison_sociale)
    c.setFont("Helvetica", 9)
    c.drawString(11.5*cm, height - 7.8*cm, f"Tél : {bc.fournisseur.telephone}")
    c.drawString(11.5*cm, height - 8.2*cm, f"Email : {bc.fournisseur.email}")

    # --- Tableau des lignes ---
    y = height - 10*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Désignation")
    c.drawString(10*cm, y, "Quantité")
    c.drawString(12.5*cm, y, "Unité")
    c.drawString(14.5*cm, y, "P.U HT")
    c.drawString(17*cm, y, "Total HT")
    
    c.line(2*cm, y-0.2*cm, 19*cm, y-0.2*cm)
    
    c.setFont("Helvetica", 9)
    y -= 0.7*cm
    for ligne in bc.lignes.all():
        c.drawString(2*cm, y, ligne.designation[:45])
        c.drawString(10*cm, y, str(ligne.quantite))
        c.drawString(12.5*cm, y, ligne.unite)
        c.drawString(14.5*cm, y, f"{ligne.prix_unitaire_ht_dzd:,.2f}")
        c.drawString(17*cm, y, f"{ligne.montant_ht_dzd:,.2f}")
        y -= 0.6*cm
        if y < 4*cm: # Nouvelle page si nécessaire (simplifié ici)
            c.showPage()
            y = height - 2*cm
            
    # --- Totaux ---
    y -= 1*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(13*cm, y, "TOTAL HT :")
    c.drawRightString(19*cm, y, f"{bc.montant_ht_dzd:,.2f} DZD")
    y -= 0.6*cm
    c.drawString(13*cm, y, f"TVA ({bc.taux_tva}%) :")
    c.drawRightString(19*cm, y, f"{bc.montant_tva_dzd:,.2f} DZD")
    y -= 0.6*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(13*cm, y, "TOTAL TTC :")
    c.drawRightString(19*cm, y, f"{bc.montant_ttc_dzd:,.2f} DZD")
    
    # --- Signature et Cachet ---
    c.setStrokeColor(colors.blue)
    c.circle(16*cm, 3.5*cm, 1.8*cm)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.blue)
    c.drawCentredString(16*cm, 3.7*cm, "APPROUVÉ")
    c.drawCentredString(16*cm, 3.3*cm, "BTP ALGERIA")
    
    c.save()
    return f"achats/bons_commande/{filename}"
