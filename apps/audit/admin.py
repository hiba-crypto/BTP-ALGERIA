from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'module', 'object_type', 'status', 'risk_level')
    list_filter = ('action', 'module', 'status', 'risk_level')
    search_fields = ('username_snapshot', 'object_id', 'object_repr')
    readonly_fields = ('timestamp', 'user', 'username_snapshot', 'ip_address', 'user_agent', 'session_key', 'action', 'module', 'object_type', 'object_id', 'object_repr', 'old_value', 'new_value', 'status', 'risk_level')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
