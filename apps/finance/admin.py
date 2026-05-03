from django.contrib import admin
from .models import CompteComptable, CompteBancaire, EcritureComptable, MouvementBancaire

@admin.register(CompteComptable)
class CompteComptableAdmin(admin.ModelAdmin):
    list_display = ('numero', 'intitule', 'type_compte', 'is_active')
    search_fields = ('numero', 'intitule')

@admin.register(CompteBancaire)
class CompteBancaireAdmin(admin.ModelAdmin):
    list_display = ('banque', 'intitule', 'devise', 'solde_dzd')

@admin.register(EcritureComptable)
class EcritureComptableAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_ecriture', 'compte_debit', 'compte_credit', 'montant_dzd')
    search_fields = ('reference', 'libelle')

@admin.register(MouvementBancaire)
class MouvementBancaireAdmin(admin.ModelAdmin):
    list_display = ('compte', 'date_valeur', 'montant_debit_dzd', 'montant_credit_dzd')
