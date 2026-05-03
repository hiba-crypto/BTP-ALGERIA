from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .models import AuditLog
from apps.accounts.decorators import module_required
import csv
from openpyxl import Workbook

class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'audit/audit_log.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres
        action = self.request.GET.get('action')
        module = self.request.GET.get('module')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        user_id = self.request.GET.get('user')

        if action:
            queryset = queryset.filter(action=action)
        if module:
            queryset = queryset.filter(module=module)
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset

class SecurityDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'audit/security_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # We would aggregate data for charts here
        context['recent_critical'] = AuditLog.objects.filter(risk_level='critical').order_by('-timestamp')[:5]
        return context

class ExportAuditView(LoginRequiredMixin, View):
    # Should be restricted to auditor/admin
    
    def get(self, request):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = "Audit Logs"
        
        columns = ['Date', 'Utilisateur', 'IP', 'Action', 'Module', 'Objet', 'Niveau de Risque', 'Statut']
        ws.append(columns)

        for log in AuditLog.objects.all()[:1000]:  # Limit for safety
            ws.append([
                log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                log.username_snapshot,
                log.ip_address,
                log.get_action_display(),
                log.module,
                log.object_repr,
                log.get_risk_level_display(),
                log.get_status_display()
            ])

        wb.save(response)
        return response
