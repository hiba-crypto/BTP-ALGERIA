from django.contrib import admin
from .models import Client, Projet, SituationTravaux, RentabiliteProjet

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'wilaya', 'contact_nom')
    search_fields = ('nom', 'contact_nom')

@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('reference', 'intitule', 'client', 'statut', 'avancement_pct')
    list_filter = ('statut', 'type_travaux', 'wilaya_chantier')
    search_fields = ('reference', 'intitule')

@admin.register(SituationTravaux)
class SituationTravauxAdmin(admin.ModelAdmin):
    list_display = ('projet', 'numero', 'mois', 'annee', 'montant_periode_ht_dzd', 'statut')
    list_filter = ('statut', 'annee')

@admin.register(RentabiliteProjet)
class RentabiliteProjetAdmin(admin.ModelAdmin):
    list_display = ('projet', 'marge_brute_dzd', 'marge_nette_dzd')
