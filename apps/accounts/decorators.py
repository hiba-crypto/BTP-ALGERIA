from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(*role_names):
    """Decorator to require specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                profile = request.user.profile
                if profile.role and profile.role.nom in role_names:
                    return view_func(request, *args, **kwargs)
            except hasattr(request.user, 'profile'):
                pass
            raise PermissionDenied("Vous n'avez pas le rôle requis pour accéder à cette ressource.")
        return _wrapped_view
    return decorator

def module_required(module_name):
    """Generic decorator to restrict access by module based on roles."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            # Example logic, expand based on actual module mapping
            allowed_roles = ['admin_systeme', 'directeur_general']
            if module_name == 'finance':
                allowed_roles.append('comptable')
            elif module_name == 'employees':
                allowed_roles.append('responsable_rh')
            elif module_name == 'projects':
                allowed_roles.extend(['chef_projet', 'technicien'])
            elif module_name == 'fleet':
                allowed_roles.extend(['chef_projet', 'responsable_parc'])
            elif module_name == 'suppliers':
                allowed_roles.extend(['chef_projet', 'responsable_achats'])
            elif module_name == 'audit':
                allowed_roles.append('auditeur')
                
            try:
                profile = request.user.profile
                if profile.role and profile.role.nom in allowed_roles:
                    return view_func(request, *args, **kwargs)
            except:
                pass
            raise PermissionDenied(f"Accès refusé au module {module_name}.")
        return _wrapped_view
    return decorator

def log_access(action_name, module_name):
    """Decorator to log sensitive views."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Simple logging, ideal implementation would be in a middleware or signal
            if request.user.is_authenticated:
                from apps.audit.models import AuditLog
                AuditLog.objects.create(
                    user=request.user,
                    username_snapshot=request.user.username,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                    session_key=request.session.session_key or '',
                    action=action_name,
                    module=module_name,
                    status='success'
                )
            return response
        return _wrapped_view
    return decorator
