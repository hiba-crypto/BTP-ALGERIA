from django.contrib import admin
from .models import Poste, Employe, DocumentEmploye, Conge, Presence, BulletinPaie
from apps.accounts.models import Wilaya

@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom_fr', 'nom_ar')
    search_fields = ('code', 'nom_fr')

@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'salaire_base_min')
    search_fields = ('titre',)

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'poste', 'statut')
    search_fields = ('matricule', 'nom', 'prenom', 'cni')
    list_filter = ('statut', 'type_contrat', 'poste')

admin.site.register(DocumentEmploye)
admin.site.register(Conge)
admin.site.register(Presence)
admin.site.register(BulletinPaie)
