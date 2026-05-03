from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='two_factor_setup'),
    path('2fa/verify/', views.TwoFactorVerifyView.as_view(), name='two_factor_verify'),
    path('password/change/', views.ChangePasswordView.as_view(), name='change_password'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('users/', views.UserManagementView.as_view(), name='user_management'),
    path('users/<int:user_id>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]
