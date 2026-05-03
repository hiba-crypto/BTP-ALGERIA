from django import forms
from .models import Employe, DocumentEmploye, Conge, Presence, Poste

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = [
            'matricule', 'nom', 'prenom', 'nom_arabe', 'date_naissance', 
            'wilaya_naissance', 'commune_naissance', 'cni', 'num_cnas', 
            'nif_fiscal', 'adresse', 'telephone', 'rib_bancaire', 'email_pro', 
            'situation_familiale', 'nb_enfants', 'contact_urgence_nom', 
            'contact_urgence_tel', 'type_contrat', 'date_embauche', 
            'date_fin_contrat', 'poste', 'wilaya_travail', 'salaire_base_crypt', 
            'mode_paiement', 'projet_affecte', 'statut'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
            'date_fin_contrat': forms.DateInput(attrs={'type': 'date'}),
            'salaire_base_crypt': forms.NumberInput(attrs={'step': '0.01'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'salaire_base_crypt': 'Salaire de Base (DZD)',
            'cni': 'N° CNI',
            'num_cnas': 'N° CNAS',
            'nif_fiscal': 'NIF',
            'rib_bancaire': 'RIB',
        }

class CongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['type_conge', 'date_debut', 'date_fin', 'motif', 'justificatif']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'motif': forms.Textarea(attrs={'rows': 3}),
        }

class PresenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ['employe', 'date', 'projet', 'heure_arrivee', 'heure_depart', 'statut', 'heures_sup', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure_arrivee': forms.TimeInput(attrs={'type': 'time'}),
            'heure_depart': forms.TimeInput(attrs={'type': 'time'}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }
