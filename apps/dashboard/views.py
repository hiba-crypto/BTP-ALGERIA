from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.db.models import Sum, Count
from apps.projects.models import Projet, SituationTravaux
from apps.finance.models import CompteBancaire, EcritureComptable
from apps.employees.models import Employe
from apps.fleet.models import Engin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os
from django.utils import timezone
from .models import PublicQuoteRequest
from django.contrib import messages

class PublicLandingView(TemplateView):
    template_name = 'public/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projets_realises'] = Projet.objects.filter(statut='termine')[:6]
        return context

    def post(self, request, *args, **kwargs):
        nom = request.POST.get('nom_complet')
        email = request.POST.get('email')
        sujet = request.POST.get('sujet')
        message = request.POST.get('message')

        if nom and email and sujet and message:
            PublicQuoteRequest.objects.create(
                nom_complet=nom,
                email=email,
                sujet=sujet,
                message=message
            )
            messages.success(request, "Votre demande a été envoyée avec succès. Notre équipe vous contactera sous peu.")
        else:
            messages.error(request, "Veuillez remplir tous les champs du formulaire.")
        
        return redirect('public_landing')

class DashboardRouterView(LoginRequiredMixin, TemplateView):
    """
    Redirects user to the correct dashboard based on their primary role/group.
    """
    def get(self, request, *args, **kwargs):
        groups = request.user.groups.values_list('name', flat=True)
        if 'dg' in groups or request.user.is_superuser:
            return redirect('dg_dashboard')
        elif 'rh' in groups:
            return redirect('rh_dashboard')
        elif 'comptable' in groups:
            return redirect('finance_dashboard')
        elif 'chef_projet' in groups:
            return redirect('projet_dashboard')
        return redirect('projet_dashboard') # Default

class DGDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dg_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # KPI
        context['ca_total'] = SituationTravaux.objects.filter(statut='payee').aggregate(Sum('montant_periode_ht_dzd'))['montant_periode_ht_dzd__sum'] or 0
        context['tresorerie'] = CompteBancaire.objects.filter(is_active=True).aggregate(Sum('solde_dzd'))['solde_dzd__sum'] or 0
        context['projets_actifs'] = Projet.objects.filter(statut='en_cours').count()
        context['effectif'] = Employe.objects.filter(statut='ACTIF').count()

        # ---- Graphique Evolution CA par mois ----
        from django.db.models.functions import TruncMonth
        import json
        ca_par_mois = (
            SituationTravaux.objects
            .filter(statut__in=['payee', 'validee'])
            .values('mois', 'annee')
            .annotate(total=Sum('montant_periode_ht_dzd'))
            .order_by('annee', 'mois')
        )
        mois_labels = []
        mois_data = []
        MOIS = ['','Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
        for entry in ca_par_mois:
            mois_labels.append(f"{MOIS[entry['mois']]} {entry['annee']}")
            mois_data.append(float(entry['total']))
        context['chart_ca_labels'] = json.dumps(mois_labels)
        context['chart_ca_data']   = json.dumps(mois_data)

        # ---- Graphique Répartition des Charges ----
        from apps.projects.models import RentabiliteProjet
        rent_stats = RentabiliteProjet.objects.aggregate(
            mo=Sum('cout_mo_dzd'),
            mat=Sum('cout_materiaux_dzd'),
            eng=Sum('cout_engins_dzd'),
            st=Sum('cout_sous_traitance_dzd'),
            fg=Sum('frais_generaux_dzd')
        )
        context['chart_budget_data'] = json.dumps([
            float(rent_stats['mo'] or 0),
            float(rent_stats['mat'] or 0),
            float(rent_stats['eng'] or 0),
            float(rent_stats['st'] or 0),
            float(rent_stats['fg'] or 0),
        ])

        # ---- Graphique Évaluation Fournisseurs (Top 5) ----
        from apps.suppliers.models import Fournisseur
        top_suppliers = Fournisseur.objects.filter(is_active=True, note_qualite__gt=0).order_by('-note_qualite')[:5]
        context['supplier_labels'] = json.dumps([s.raison_sociale[:20] for s in top_suppliers])
        context['supplier_notes']  = json.dumps([float(s.note_qualite) for s in top_suppliers])

        # Projets for progress bars
        context['projets'] = Projet.objects.filter(is_active=True)
        context['projets_json'] = json.dumps([
            {'ref': p.reference, 'pct': float(p.avancement_pct)} for p in context['projets']
        ])

        # Demandes de contact externes
        context['demandes_externes'] = PublicQuoteRequest.objects.filter(est_traite=False).order_by('-date_envoi')

        return context

class RHDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/rh_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['effectif_total'] = Employe.objects.filter(statut='ACTIF').count()
        # Add more RH specific KPIs here
        return context

class FinanceDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/finance_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comptes'] = CompteBancaire.objects.all()
        context['total_cash'] = context['comptes'].aggregate(Sum('solde_dzd'))['solde_dzd__sum'] or 0
        return context

class ProjetDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/projet_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projets'] = Projet.objects.all()
        return context

class NotificationsListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/notifications.html'

def export_dg_report_pdf(request):
    """
    Génère un rapport PDF global pour la Direction Générale.
    """
    if not (request.user.is_superuser or request.user.groups.filter(name='dg').exists()):
        return HttpResponse("Accès refusé", status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Rapport_Global_BTP_Algeria.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # En-tête
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "BTP ALGERIA SPA - RAPPORT GLOBAL")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 2.6*cm, f"Généré le : {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    c.line(2*cm, height - 3*cm, 19*cm, height - 3*cm)

    # Section KPI
    y = height - 4*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, "Indicateurs de Performance (KPI)")
    y -= 1*cm
    c.setFont("Helvetica", 12)
    
    ca_total = SituationTravaux.objects.filter(statut='payee').aggregate(Sum('montant_periode_ht_dzd'))['montant_periode_ht_dzd__sum'] or 0
    tresorerie = CompteBancaire.objects.filter(is_active=True).aggregate(Sum('solde_dzd'))['solde_dzd__sum'] or 0
    projets_count = Projet.objects.filter(statut='en_cours').count()
    effectif = Employe.objects.filter(statut='ACTIF').count()

    c.drawString(3*cm, y, f"- Chiffre d'Affaires Total (Encaissé) : {ca_total:,.2f} DZD")
    y -= 0.8*cm
    c.drawString(3*cm, y, f"- Trésorerie Disponible : {tresorerie:,.2f} DZD")
    y -= 0.8*cm
    c.drawString(3*cm, y, f"- Nombre de Projets en cours : {projets_count}")
    y -= 0.8*cm
    c.drawString(3*cm, y, f"- Effectif Total Actif : {effectif} employés")
    
    # Section Projets
    y -= 1.5*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, "État d'Avancement des Projets")
    y -= 1*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2.5*cm, y, "Référence")
    c.drawString(5*cm, y, "Intitulé")
    c.drawString(14*cm, y, "Avancement")
    c.line(2*cm, y-0.2*cm, 19*cm, y-0.2*cm)
    
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    for p in Projet.objects.filter(is_active=True):
        c.drawString(2.5*cm, y, p.reference)
        c.drawString(5*cm, y, p.intitule[:45])
        c.drawString(14*cm, y, f"{p.avancement_pct}%")
        y -= 0.6*cm
        if y < 3*cm:
            c.showPage()
            y = height - 2*cm

    c.showPage()
    c.save()
    return response
