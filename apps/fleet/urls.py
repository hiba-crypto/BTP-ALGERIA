from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.FleetDashboardView.as_view(), name='fleet_dashboard'),
    path('engins/', views.EnginListView.as_view(), name='engin_list'),
    path('engins/add/', views.EnginCreateView.as_view(), name='engin_add'),
    path('engins/<int:pk>/', views.EnginDetailView.as_view(), name='engin_detail'),
    path('engins/<int:pk>/edit/', views.EnginUpdateView.as_view(), name='engin_edit'),
    
    path('maintenance/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenance/add/', views.MaintenanceCreateView.as_view(), name='maintenance_add'),
    
    path('carburant/', views.BonCarburantListView.as_view(), name='carburant_list'),
    path('carburant/add/', views.BonCarburantCreateView.as_view(), name='carburant_add'),
    path('allocation/<int:projet_id>/', views.AllocationCreateView.as_view(), name='allocation_create'),
]
