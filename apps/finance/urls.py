from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.FinanceTableauBordView.as_view(), name='finance_dashboard'),
    path('ecritures/', views.EcritureComptableListView.as_view(), name='ecriture_list'),
    path('ecritures/add/', views.EcritureComptableCreateView.as_view(), name='ecriture_add'),
    path('banques/', views.CompteBancaireView.as_view(), name='compte_bancaire_list'),
    path('banques/add/', views.CompteBancaireCreateView.as_view(), name='compte_bancaire_add'),
    path('banques/<int:pk>/edit/', views.CompteBancaireUpdateView.as_view(), name='compte_bancaire_edit'),
]
