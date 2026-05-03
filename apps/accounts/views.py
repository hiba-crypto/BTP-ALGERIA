from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView, PasswordChangeView
from django.contrib.auth import login, update_session_auth_hash
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import LoginForm, TwoFactorForm, CustomPasswordChangeForm, UserCreateForm, UserUpdateForm
from .models import UserProfile, Role
from apps.audit.models import AuditLog
from axes.utils import reset
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
import datetime
import pyotp
import qrcode
import io
import base64

class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        profile, created = UserProfile.objects.get_or_create(user=user)

        # Check if locked
        if profile.locked_until and profile.locked_until > timezone.now():
            messages.error(self.request, "Compte bloqué temporairement suite à trop d'échecs.")
            return render(self.request, self.template_name, {'form': form})
        
        # Audit Log
        AuditLog.objects.create(
            user=user,
            username_snapshot=user.username,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:255],
            action='LOGIN_SUCCESS',
            module='admin',
            status='success'
        )

        # Reset failed login count
        profile.failed_login_count = 0
        profile.locked_until = None
        profile.last_login_ip = self.request.META.get('REMOTE_ADDR')
        profile.last_login_ua = self.request.META.get('HTTP_USER_AGENT', '')[:255]
        profile.save()
        reset(username=user.username)

        # 2FA check
        if profile.two_fa_enabled:
            self.request.session['pre_2fa_user_id'] = user.id
            return redirect('two_factor_verify')

        login(self.request, user)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        username = self.request.POST.get('username')
        # Audit Log
        AuditLog.objects.create(
            username_snapshot=username,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            action='LOGIN_FAIL',
            module='admin',
            status='failed'
        )
        return super().form_invalid(form)

class LogoutView(AuthLogoutView):
    next_page = 'login'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                username_snapshot=request.user.username,
                action='LOGOUT',
                module='admin',
                status='success'
            )
        return super().dispatch(request, *args, **kwargs)

class TwoFactorVerifyView(View):
    def get(self, request):
        if 'pre_2fa_user_id' not in request.session:
            return redirect('login')
        form = TwoFactorForm()
        return render(request, 'accounts/two_factor.html', {'form': form})

    def post(self, request):
        if 'pre_2fa_user_id' not in request.session:
            return redirect('login')
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User
            user = User.objects.get(id=request.session['pre_2fa_user_id'])
            profile = user.profile
            totp = pyotp.TOTP(profile.two_fa_secret)
            if totp.verify(form.cleaned_data['code']):
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                return redirect('dashboard_router')
            else:
                messages.error(request, "Code invalide.")
        return render(request, 'accounts/two_factor.html', {'form': form})

class TwoFactorSetupView(LoginRequiredMixin, View):
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if not profile.two_fa_secret:
            profile.two_fa_secret = pyotp.random_base32()
            profile.save()
        
        totp = pyotp.TOTP(profile.two_fa_secret)
        url = totp.provisioning_uri(name=request.user.email, issuer_name="BTP Algeria")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_image = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return render(request, 'accounts/two_factor_setup.html', {'qr_image': qr_image})

    def post(self, request):
        code = request.POST.get('code')
        profile = request.user.profile
        totp = pyotp.TOTP(profile.two_fa_secret)
        if totp.verify(code):
            profile.two_fa_enabled = True
            profile.save()
            messages.success(request, "2FA activé avec succès.")
            return redirect('profile')
        messages.error(request, "Code invalide.")
        return self.get(request)

class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, "Mot de passe mis à jour avec succès.")
        profile = self.request.user.profile
        profile.must_change_password = False
        profile.last_password_change = timezone.now()
        profile.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        try:
            return self.request.user.profile.role.nom == 'admin'
        except:
            return False

class UserManagementView(AdminRequiredMixin, TemplateView):
    template_name = 'accounts/user_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '')
        role_filter = self.request.GET.get('role', '')
        
        users = User.objects.select_related('profile__role').all().order_by('username')
        
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            ).distinct()
            
        if role_filter:
            users = users.filter(profile__role_id=role_filter)
        
        context['users'] = users.order_by('username')
        context['roles'] = Role.objects.all()
        context['form'] = UserCreateForm()
        context['search_query'] = search_query
        context['role_filter'] = int(role_filter) if role_filter and role_filter.isdigit() else ''
        return context

    def post(self, request, *args, **kwargs):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur créé avec succès.")
            return redirect('user_management')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_edit.html'
    success_url = reverse_lazy('user_management')
    pk_url_kwarg = 'user_id'

    def form_valid(self, form):
        messages.success(self.request, "Utilisateur mis à jour.")
        return super().form_valid(form)

class UserDeleteView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        if user == request.user:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        else:
            user.delete()
            messages.success(request, "Utilisateur supprimé.")
        return redirect('user_management')
