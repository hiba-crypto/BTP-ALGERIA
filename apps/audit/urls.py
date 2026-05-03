from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.AuditLogListView.as_view(), name='audit_logs'),
    path('dashboard/', views.SecurityDashboardView.as_view(), name='security_dashboard'),
    path('export/', views.ExportAuditView.as_view(), name='export_audit_logs'),
]
