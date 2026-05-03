from django import forms
from .models import CompteComptable, EcritureComptable, CompteBancaire
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class EcritureComptableForm(forms.ModelForm):
    class Meta:
        model = EcritureComptable
        fields = ['date_ecriture', 'libelle', 'compte_debit', 'compte_credit', 'montant_dzd', 'projet', 'piece_justificative', 'statut']
        widgets = {
            'date_ecriture': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Enregistrer Écriture'))
