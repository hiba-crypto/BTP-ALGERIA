from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class GroupRequiredMixin(UserPassesTestMixin):
    """
    Mixin to require one of multiple groups/roles.
    Usage:
        class MyView(GroupRequiredMixin, ListView):
            required_groups = ['admin', 'rh']
    """
    required_groups = []

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        user_groups = self.request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in self.required_groups)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return super().handle_no_permission()

class RoleRequiredMixin(GroupRequiredMixin):
    """Alias for GroupRequiredMixin for future role migration if needed."""
    @property
    def required_roles(self):
        return self.required_groups
    
    @required_roles.setter
    def required_roles(self, value):
        self.required_groups = value
