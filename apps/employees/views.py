from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.accounts.mixins import GroupRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
import datetime

from .models import Employe, Conge, Presence, BulletinPaie
from .forms import EmployeForm, CongeForm, PresenceForm
from .utils import calculer_bulletin, generer_pdf_bulletin
from apps.audit.utils import log_action

class EmployeListView(GroupRequiredMixin, ListView):
    required_groups = ['admin', 'dg', 'rh', 'chef_projet', 'comptable']
    model = Employe
    template_name = 'employees/employee_list.html'
    context_object_name = 'employes'
    
    def get_queryset(self):
        qs = Employe.objects.filter(is_active=True)
        # Filters logic could go here
        return qs

class EmployeDetailView(GroupRequiredMixin, DetailView):
    required_groups = ['admin', 'dg', 'rh', 'chef_projet', 'comptable']
    model = Employe
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employe'

class EmployeCreateView(GroupRequiredMixin, CreateView):
    required_groups = ['admin', 'rh']
    model = Employe
    form_class = EmployeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employee_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Employé créé avec succès.")
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action='CREATE',
            module='rh',
            object_type='Employe',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request
        )
        return response

class EmployeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employe
    form_class = EmployeForm
    template_name = 'employees/employee_form.html'
    
    def get_success_url(self):
        return reverse_lazy('employee_detail', kwargs={'pk': self.object.pk})
        
    def form_valid(self, form):
        messages.success(self.request, "Employé mis à jour avec succès.")
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action='UPDATE',
            module='rh',
            object_type='Employe',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request
        )
        return response

class EmployeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employe
    success_url = reverse_lazy('employee_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        log_action(
            user=self.request.user,
            action='DELETE',
            module='rh',
            object_type='Employe',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request,
            status='success',
            risk_level='medium'
        )
        messages.success(self.request, "Employé supprimé (archivé).")
        return redirect(self.success_url)

# --- CONGES ---

class CongeListView(LoginRequiredMixin, ListView):
    model = Conge
    template_name = 'employees/leave_list.html'
    context_object_name = 'conges'
    ordering = ['-created_at']

class CongeCreateView(LoginRequiredMixin, CreateView):
    model = Conge
    form_class = CongeForm
    template_name = 'employees/leave_form.html'
    success_url = reverse_lazy('leave_list')
    
    def form_valid(self, form):
        # Pour simplifier, on prend le premier employé (dans la réalité: l'utilisateur connecté ou sélection via URL)
        form.instance.employe = Employe.objects.first() 
        messages.success(self.request, "Demande de congé soumise.")
        return super().form_valid(form)

class CongeApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        conge = get_object_or_404(Conge, pk=pk)
        conge.statut = 'approuve'
        conge.approuve_par = request.user
        conge.save()
        messages.success(request, f"Congé {conge.id} approuvé.")
        return redirect('leave_list')

# --- PRESENCES ---

class PresenceListView(LoginRequiredMixin, ListView):
    model = Presence
    template_name = 'employees/attendance_list.html'
    context_object_name = 'presences'
    ordering = ['-date']

class PresenceBulkCreateView(LoginRequiredMixin, CreateView):
    model = Presence
    form_class = PresenceForm
    template_name = 'employees/attendance_form.html'
    success_url = reverse_lazy('attendance_list')

# --- PAIE ---

class BulletinPaieListView(GroupRequiredMixin, ListView):
    required_groups = ['admin', 'dg', 'rh', 'comptable']
    model = BulletinPaie
    template_name = 'employees/payroll_list.html'
    context_object_name = 'bulletins'
    ordering = ['-annee', '-mois']

class BulletinPaieGenerateView(LoginRequiredMixin, View):
    def post(self, request):
        mois = int(request.POST.get('mois', datetime.date.today().month))
        annee = int(request.POST.get('annee', datetime.date.today().year))
        
        employes = Employe.objects.filter(is_active=True, statut='actif')
        for emp in employes:
            if not BulletinPaie.objects.filter(employe=emp, mois=mois, annee=annee).exists():
                calc = calculer_bulletin(emp, mois, annee)
                BulletinPaie.objects.create(
                    employe=emp,
                    mois=mois,
                    annee=annee,
                    salaire_base=calc['salaire_base'],
                    prime_anciennete=calc['prime_anciennete'],
                    salaire_brut=calc['salaire_brut'],
                    cnas_salariale=calc['cnas'],
                    irg=calc['irg'],
                    cacobatph_salariale=calc['cacobatph'],
                    salaire_net=calc['salaire_net'],
                    created_by=request.user
                )
        messages.success(request, f"Bulletins générés pour {mois}/{annee}.")
        return redirect('payroll_list')

class BulletinPaieDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        bulletin = get_object_or_404(BulletinPaie, pk=pk)
        if not bulletin.pdf_file:
            pdf_path = generer_pdf_bulletin(bulletin)
            bulletin.pdf_file.name = pdf_path
            bulletin.save()
            
        with open(bulletin.pdf_file.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="bulletin_{bulletin.id}.pdf"'
            return response
