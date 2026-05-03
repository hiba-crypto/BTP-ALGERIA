from django import forms
from .models import Fournisseur, DocumentFournisseur, DemandeAchat, DevisComparaison, BonCommande, LigneBonCommande, BonReception, FactureFournisseur

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        exclude = ['code', 'created_by', 'is_active']
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'forme_juridique': forms.Select(attrs={'class': 'form-select'}),
            'registre_commerce': forms.TextInput(attrs={'class': 'form-control'}),
            'nif': forms.TextInput(attrs={'class': 'form-control'}),
            'nis': forms.TextInput(attrs={'class': 'form-control'}),
            'article_imposition': forms.TextInput(attrs={'class': 'form-control'}),
            'wilaya': forms.Select(attrs={'class': 'form-select'}),
            'commune': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'fax': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'site_web': forms.URLInput(attrs={'class': 'form-control'}),
            'domaines': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'note_qualite': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '5', 'step': '0.1'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'motif_blacklist': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'delai_moyen_livraison': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DemandeAchatForm(forms.ModelForm):
    class Meta:
        model = DemandeAchat
        exclude = ['reference', 'statut', 'demandeur', 'approuve_par', 'date_approbation', 'motif_rejet']
        widgets = {
            'objet': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'unite': forms.TextInput(attrs={'class': 'form-control'}),
            'montant_estime_dzd': forms.NumberInput(attrs={'class': 'form-control'}),
            'urgence': forms.Select(attrs={'class': 'form-select'}),
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class DevisComparaisonForm(forms.ModelForm):
    class Meta:
        model = DevisComparaison
        fields = '__all__'
        widgets = {
            'demande': forms.HiddenInput(),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'montant_ht_dzd': forms.NumberInput(attrs={'class': 'form-control'}),
            'taux_tva': forms.NumberInput(attrs={'class': 'form-control'}),
            'delai_livraison_jours': forms.NumberInput(attrs={'class': 'form-control'}),
            'conditions_paiement': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fichier_devis': forms.FileInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class BonCommandeForm(forms.ModelForm):
    class Meta:
        model = BonCommande
        exclude = ['reference', 'statut', 'approuve_par', 'pdf_file', 'created_by']
        widgets = {
            'demande': forms.Select(attrs={'class': 'form-select'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'date_livraison_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'montant_ht_dzd': forms.NumberInput(attrs={'class': 'form-control'}),
            'taux_tva': forms.NumberInput(attrs={'class': 'form-control'}),
            'conditions_paiement': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'lieu_livraison': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class LigneBonCommandeForm(forms.ModelForm):
    class Meta:
        model = LigneBonCommande
        fields = ['designation', 'reference_article', 'quantite', 'unite', 'prix_unitaire_ht_dzd']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_article': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'unite': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_unitaire_ht_dzd': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BonReceptionForm(forms.ModelForm):
    class Meta:
        model = BonReception
        exclude = ['reference', 'receptionnaire']
        widgets = {
            'bon_commande': forms.Select(attrs={'class': 'form-select'}),
            'date_reception': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class FactureFournisseurForm(forms.ModelForm):
    class Meta:
        model = FactureFournisseur
        exclude = ['montant_tva_dzd', 'montant_ttc_dzd', 'montant_paye_dzd', 'solde_dzd', 'created_by']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'bon_commande': forms.Select(attrs={'class': 'form-select'}),
            'bon_reception': forms.Select(attrs={'class': 'form-select'}),
            'date_facture': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'montant_ht_dzd': forms.NumberInput(attrs={'class': 'form-control'}),
            'taux_tva': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'fichier_facture': forms.FileInput(attrs={'class': 'form-control'}),
        }
