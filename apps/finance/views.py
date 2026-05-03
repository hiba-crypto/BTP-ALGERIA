from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import EcritureComptable, CompteBancaire
from django.db.models import Sum

class FinanceTableauBordView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/tableau_bord.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comptes = CompteBancaire.objects.filter(is_active=True)
        context['comptes'] = comptes
        context['tresorerie_totale'] = comptes.aggregate(Sum('solde_dzd'))['solde_dzd__sum'] or 0
        context['dernieres_ecritures'] = EcritureComptable.objects.order_by('-date_ecriture', '-id')[:10]
        return context

class EcritureComptableListView(LoginRequiredMixin, ListView):
    model = EcritureComptable
    template_name = 'finance/ecriture_list.html'
    context_object_name = 'ecritures'
    paginate_by = 50

class CompteBancaireView(LoginRequiredMixin, ListView):
    model = CompteBancaire
    template_name = 'finance/compte_bancaire_list.html'
    context_object_name = 'comptes'

class EcritureComptableCreateView(LoginRequiredMixin, CreateView):
    model = EcritureComptable
    fields = ['reference', 'date_ecriture', 'libelle', 'compte_debit', 'compte_credit', 'montant_dzd', 'projet', 'statut']
    template_name = 'finance/ecriture_form.html'
    success_url = reverse_lazy('ecriture_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CompteBancaireCreateView(LoginRequiredMixin, CreateView):
    model = CompteBancaire
    fields = ['banque', 'intitule', 'numero_compte', 'rib', 'solde_dzd', 'devise', 'is_active']
    template_name = 'finance/compte_bancaire_form.html'
    success_url = reverse_lazy('compte_bancaire_list')

class CompteBancaireUpdateView(LoginRequiredMixin, UpdateView):
    model = CompteBancaire
    fields = ['banque', 'intitule', 'numero_compte', 'rib', 'solde_dzd', 'devise', 'is_active']
    template_name = 'finance/compte_bancaire_form.html'
    success_url = reverse_lazy('compte_bancaire_list')
