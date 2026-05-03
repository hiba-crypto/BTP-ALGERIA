from django.urls import path
from . import views

urlpatterns = [
    path('', views.EmployeListView.as_view(), name='employee_list'),
    path('nouveau/', views.EmployeCreateView.as_view(), name='employee_create'),
    path('<int:pk>/', views.EmployeDetailView.as_view(), name='employee_detail'),
    path('<int:pk>/modifier/', views.EmployeUpdateView.as_view(), name='employee_update'),
    path('<int:pk>/supprimer/', views.EmployeDeleteView.as_view(), name='employee_delete'),
    
    path('conges/', views.CongeListView.as_view(), name='leave_list'),
    path('conges/nouveau/', views.CongeCreateView.as_view(), name='leave_create'),
    path('conges/<int:pk>/approuver/', views.CongeApproveView.as_view(), name='leave_approve'),
    
    path('presences/', views.PresenceListView.as_view(), name='attendance_list'),
    path('presences/saisie/', views.PresenceBulkCreateView.as_view(), name='attendance_create'),
    
    path('paie/', views.BulletinPaieListView.as_view(), name='payroll_list'),
    path('paie/generer/', views.BulletinPaieGenerateView.as_view(), name='payroll_generate'),
    path('paie/<int:pk>/pdf/', views.BulletinPaieDownloadView.as_view(), name='payroll_download'),
]
