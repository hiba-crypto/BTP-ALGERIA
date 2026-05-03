from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjetListView.as_view(), name='projet_list'),
    path('nouveau/', views.ProjetCreateView.as_view(), name='projet_create'),
    path('<int:pk>/', views.ProjetDetailView.as_view(), name='projet_detail'),
    path('<int:pk>/modifier/', views.ProjetUpdateView.as_view(), name='projet_update'),
    path('<int:projet_id>/situation/nouvelle/', views.SituationTravauxCreateView.as_view(), name='situation_create'),
    path('<int:pk>/rentabilite/', views.RentabiliteView.as_view(), name='projet_rentabilite'),
]
