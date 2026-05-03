from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from .models import Engin, Maintenance, BonCarburant, AllocationEngin
from .utils import generer_alertes_flotte
from django.db.models import Sum
from django.shortcuts import redirect
import datetime
from apps.audit.utils import log_action

class FleetDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'fleet/fleet_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_engins'] = Engin.objects.filter(is_active=True).count()
        context['en_service'] = Engin.objects.filter(etat='en_service').count()
        context['en_maintenance'] = Engin.objects.filter(etat='en_maintenance').count()
        context['alertes'] = generer_alertes_flotte()
        
        # Coûts totaux
        context['cout_maintenance'] = Maintenance.objects.filter(statut='terminee').aggregate(Sum('cout_total_dzd'))['cout_total_dzd__sum'] or 0
        context['cout_carburant'] = BonCarburant.objects.aggregate(Sum('montant_dzd'))['montant_dzd__sum'] or 0
        
        return context

class EnginListView(LoginRequiredMixin, ListView):
    model = Engin
    template_name = 'fleet/engin_list.html'
    context_object_name = 'engins'

class EnginDetailView(LoginRequiredMixin, DetailView):
    model = Engin
    template_name = 'fleet/engin_detail.html'
    context_object_name = 'engin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maintenances'] = self.object.maintenances.all().order_by('-date_entree')
        context['carburants'] = self.object.carburants.all().order_by('-date')
        context['allocations'] = self.object.allocations.all().order_by('-date_debut')
        return context

class EnginCreateView(LoginRequiredMixin, CreateView):
    model = Engin
    fields = ['designation', 'type_engin', 'marque', 'modele', 'numero_serie', 'immatriculation', 'annee_fabrication', 'annee_mise_en_service', 'valeur_achat_dzd', 'taux_amortissement_annuel', 'etat']
    template_name = 'fleet/engin_form.html'
    success_url = reverse_lazy('engin_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Engin ajouté avec succès.")
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action='CREATE',
            module='parc',
            object_type='Engin',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request
        )
        return response

class EnginUpdateView(LoginRequiredMixin, UpdateView):
    model = Engin
    fields = ['designation', 'type_engin', 'marque', 'modele', 'numero_serie', 'immatriculation', 'etat', 'compteur_heures', 'compteur_km']
    template_name = 'fleet/engin_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Engin mis à jour avec succès.")
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action='UPDATE',
            module='parc',
            object_type='Engin',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('engin_detail', kwargs={'pk': self.object.pk})

class EnginDeleteView(LoginRequiredMixin, DeleteView):
    model = Engin
    template_name = 'fleet/engin_confirm_delete.html'
    success_url = reverse_lazy('engin_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(
            user=self.request.user,
            action='DELETE',
            module='parc',
            object_type='Engin',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request,
            risk_level='medium'
        )
        messages.success(request, "Engin supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    fields = '__all__'
    template_name = 'fleet/maintenance_form.html'
    success_url = reverse_lazy('maintenance_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Mettre à jour l'état de l'engin
        engin = form.instance.engin
        engin.etat = 'en_maintenance'
        engin.save()
        return super().form_valid(form)

class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'fleet/maintenance_list.html'
    context_object_name = 'maintenances'

class BonCarburantCreateView(LoginRequiredMixin, CreateView):
    model = BonCarburant
    fields = '__all__'
    template_name = 'fleet/carburant_form.html'
    success_url = reverse_lazy('carburant_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class BonCarburantListView(LoginRequiredMixin, ListView):
    model = BonCarburant
    template_name = 'fleet/carburant_list.html'
    context_object_name = 'bons'

class AllocationCreateView(LoginRequiredMixin, View):
    """Create an engine allocation for a specific project via a POST form."""
    def post(self, request, projet_id):
        from apps.projects.models import Projet
        projet = get_object_or_404(Projet, pk=projet_id)
        engin_id = request.POST.get('engin')
        taux = request.POST.get('taux_journalier_dzd', 10000)
        date_debut = request.POST.get('date_debut', datetime.date.today())
        
        engin = get_object_or_404(Engin, pk=engin_id)
        AllocationEngin.objects.get_or_create(
            engin=engin, projet=projet,
            defaults={'date_debut': date_debut, 'taux_journalier_dzd': taux}
        )
        engin.projet_actuel = projet
        engin.etat = 'en_service'
        engin.save()
        messages.success(request, f"Engin {engin.code} alloué au projet {projet.reference}.")
        return redirect('projet_detail', pk=projet_id)

    def get(self, request, projet_id):
        from apps.projects.models import Projet
        projet = get_object_or_404(Projet, pk=projet_id)
        engins_disponibles = Engin.objects.filter(is_active=True).exclude(
            allocations__projet=projet
        )
        return render(request, 'fleet/allocation_form.html', {
            'projet': projet,
            'engins': engins_disponibles,
        })
