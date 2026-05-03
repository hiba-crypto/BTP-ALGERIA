from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.accounts.mixins import GroupRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Projet, SituationTravaux, RentabiliteProjet
from .forms import ProjetForm, SituationTravauxForm
from apps.finance.utils import calculer_rentabilite_projet
from apps.audit.utils import log_action

class ProjetListView(GroupRequiredMixin, ListView):
    required_groups = ['admin', 'dg', 'chef_projet', 'achats', 'parc', 'comptable']
    model = Projet
    template_name = 'projects/projet_list.html'
    context_object_name = 'projets'

class ProjetDetailView(LoginRequiredMixin, DetailView):
    model = Projet
    template_name = 'projects/projet_detail.html'
    context_object_name = 'projet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['situations'] = self.object.situations.all()
        context['allocations'] = self.object.allocations_engins.all()
        # Achats (Bons de commande et Demandes) linked to this project
        from apps.suppliers.models import BonCommande, DemandeAchat
        context['achats'] = BonCommande.objects.filter(projet=self.object).order_by('-date_commande')
        context['demandes_achat'] = DemandeAchat.objects.filter(projet=self.object).order_by('-created_at')
        # Ensure rentabilité object exists
        calculer_rentabilite_projet(self.object)
        context['rentabilite'] = self.object.rentabilite
        return context

class ProjetCreateView(GroupRequiredMixin, CreateView):
    required_groups = ['admin', 'dg', 'chef_projet']
    model = Projet
    form_class = ProjetForm
    template_name = 'projects/projet_form.html'
    success_url = reverse_lazy('projet_list')

    def form_valid(self, form):
        # Generate PRJ reference
        import datetime
        year = datetime.datetime.now().year
        count = Projet.objects.filter(reference__startswith=f'PRJ-{year}').count() + 1
        form.instance.reference = f"PRJ-{year}-{count:04d}"
        form.instance.created_by = self.request.user
        messages.success(self.request, "Projet créé avec succès.")
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action='CREATE',
            module='chef_projet',
            object_type='Projet',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request
        )
        return response

class ProjetUpdateView(LoginRequiredMixin, UpdateView):
    model = Projet
    form_class = ProjetForm
    template_name = 'projects/projet_form.html'
    
    def get_success_url(self):
        return reverse_lazy('projet_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Projet mis à jour avec succès.")
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action='UPDATE',
            module='chef_projet',
            object_type='Projet',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request
        )
        return response

class SituationTravauxCreateView(GroupRequiredMixin, CreateView):
    required_groups = ['admin', 'dg', 'chef_projet', 'comptable']
    model = SituationTravaux
    form_class = SituationTravauxForm
    template_name = 'projects/situation_form.html'

    def form_valid(self, form):
        projet = get_object_or_404(Projet, pk=self.kwargs['projet_id'])
        form.instance.projet = projet
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Update profitability
        calculer_rentabilite_projet(projet)
        
        # Update project progress based on cumul
        if projet.montant_marche_ht_dzd > 0:
            projet.avancement_pct = (form.instance.montant_cumul_ht_dzd / projet.montant_marche_ht_dzd) * 100
            projet.save()
            
        messages.success(self.request, "Situation de travaux créée.")
        return response

    def get_success_url(self):
        return reverse_lazy('projet_detail', kwargs={'pk': self.kwargs['projet_id']})

class RentabiliteView(GroupRequiredMixin, DetailView):
    required_groups = ['admin', 'dg']
    model = Projet
    template_name = 'projects/rentabilite_dashboard.html'
    context_object_name = 'projet'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calculer_rentabilite_projet(self.object)
        context['rentabilite'] = self.object.rentabilite
        return context

class ProjetDeleteView(GroupRequiredMixin, DeleteView):
    required_groups = ['admin', 'dg']
    model = Projet
    template_name = 'projects/projet_confirm_delete.html'
    success_url = reverse_lazy('projet_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(
            user=self.request.user,
            action='DELETE',
            module='chef_projet',
            object_type='Projet',
            object_id=self.object.pk,
            object_repr=str(self.object),
            request=self.request,
            risk_level='medium'
        )
        messages.success(request, "Projet supprimé avec succès.")
        return super().delete(request, *args, **kwargs)
