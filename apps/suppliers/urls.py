from django.urls import path
from . import views

urlpatterns = [
    # Fournisseurs
    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/create/', views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/', views.fournisseur_detail, name='fournisseur_detail'),
    path('fournisseurs/<int:pk>/edit/', views.fournisseur_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/delete/', views.fournisseur_delete, name='fournisseur_delete'),
    
    # Demandes d'achat
    path('achats/demandes/', views.demande_achat_list, name='demande_achat_list'),
    path('achats/demandes/create/', views.demande_achat_create, name='demande_achat_create'),
    path('achats/demandes/<int:pk>/soumettre/', views.demande_achat_soumettre, name='demande_achat_soumettre'),
    path('achats/demandes/<int:pk>/approuver/', views.demande_achat_approuver, name='demande_achat_approuver'),
    
    # Devis
    path('achats/demandes/<int:pk>/comparaison/', views.devis_comparaison, name='devis_comparaison'),
    path('achats/demandes/<int:da_pk>/devis/nouveau/', views.devis_create, name='devis_create'),
    
    # Bons de Commande
    path('achats/bc/', views.bon_commande_list, name='bon_commande_list'),
    path('achats/bc/create/', views.bon_commande_create, name='bon_commande_create'),
    path('achats/bc/create/da/<int:demande_pk>/', views.bon_commande_create, name='bon_commande_create_from_da'),
    path('achats/bc/<int:pk>/', views.bon_commande_detail, name='bon_commande_detail'),
    path('achats/bc/<int:pk>/valider/', views.bon_commande_valider, name='bon_commande_valider'),
    
    # Factures
    path('achats/factures/', views.facture_list, name='facture_list'),
    path('achats/factures/create/', views.facture_create, name='facture_create'),
]
