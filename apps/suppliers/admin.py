from django.contrib import admin
from .models import Fournisseur, DomaineActivite, DemandeAchat, BonCommande, BonReception, FactureFournisseur

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('code', 'raison_sociale', 'wilaya', 'statut')
    list_filter = ('statut', 'forme_juridique')
    search_fields = ('code', 'raison_sociale')

@admin.register(DomaineActivite)
class DomaineActiviteAdmin(admin.ModelAdmin):
    list_display = ('nom',)

@admin.register(DemandeAchat)
class DemandeAchatAdmin(admin.ModelAdmin):
    list_display = ('reference', 'projet', 'demandeur', 'statut', 'created_at')
    list_filter = ('statut', 'urgence')

@admin.register(BonCommande)
class BonCommandeAdmin(admin.ModelAdmin):
    list_display = ('reference', 'fournisseur', 'projet', 'montant_ttc_dzd', 'statut')
    list_filter = ('statut',)

@admin.register(BonReception)
class BonReceptionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'bon_commande', 'date_reception', 'statut')

@admin.register(FactureFournisseur)
class FactureFournisseurAdmin(admin.ModelAdmin):
    list_display = ('reference', 'fournisseur', 'montant_ttc_dzd', 'statut')
    list_filter = ('statut',)
