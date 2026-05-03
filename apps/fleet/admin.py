from django.contrib import admin
from .models import TypeEngin, Engin, AllocationEngin, Maintenance, BonCarburant

@admin.register(TypeEngin)
class TypeEnginAdmin(admin.ModelAdmin):
    list_display = ('nom', 'consommation_ref_lh')

@admin.register(Engin)
class EnginAdmin(admin.ModelAdmin):
    list_display = ('code', 'designation', 'type_engin', 'etat', 'projet_actuel')
    list_filter = ('etat', 'type_engin')
    search_fields = ('code', 'designation', 'numero_serie')

@admin.register(AllocationEngin)
class AllocationEnginAdmin(admin.ModelAdmin):
    list_display = ('engin', 'projet', 'date_debut', 'date_fin', 'cout_total_dzd')

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('reference', 'engin', 'type_maintenance', 'date_entree', 'statut')
    list_filter = ('statut', 'type_maintenance')

@admin.register(BonCarburant)
class BonCarburantAdmin(admin.ModelAdmin):
    list_display = ('reference', 'engin', 'date', 'quantite_litres', 'montant_dzd')
