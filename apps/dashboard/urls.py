from django.urls import path
from . import views

urlpatterns = [
    path('', views.PublicLandingView.as_view(), name='public_landing'),
    path('dashboard/', views.DashboardRouterView.as_view(), name='dashboard_router'),
    path('dg/', views.DGDashboardView.as_view(), name='dg_dashboard'),
    path('rh/', views.RHDashboardView.as_view(), name='rh_dashboard'),
    path('finance/', views.FinanceDashboardView.as_view(), name='finance_dashboard'),
    path('projets/', views.ProjetDashboardView.as_view(), name='projet_dashboard'),
    path('notifications/', views.NotificationsListView.as_view(), name='notifications'),
    path('dg/export-pdf/', views.export_dg_report_pdf, name='export_dg_report_pdf'),
]
