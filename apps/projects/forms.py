from django import forms
from .models import Projet, SituationTravaux
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        exclude = ['reference', 'montant_marche_ttc_dzd', 'date_fin_contractuelle', 'avancement_pct', 'created_by']
        widgets = {
            'date_ordre_service': forms.DateInput(attrs={'type': 'date'}),
            'date_fin_reelle_prevue': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Enregistrer le Projet'))

class SituationTravauxForm(forms.ModelForm):
    class Meta:
        model = SituationTravaux
        fields = ['numero', 'mois', 'annee', 'montant_cumul_ht_dzd', 'montant_periode_ht_dzd', 'avance_demarrage_dzd', 'statut']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Soumettre la Situation'))
