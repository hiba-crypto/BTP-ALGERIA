from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Fournisseur, DemandeAchat, DevisComparaison, BonCommande, LigneBonCommande, BonReception, FactureFournisseur
from .forms import FournisseurForm, DemandeAchatForm, BonCommandeForm, BonReceptionForm, FactureFournisseurForm, DevisComparaisonForm
from .utils import generer_pdf_bon_commande, verifier_seuil_approbation
from django.utils import timezone

# --- Fournisseurs ---
@login_required
def fournisseur_list(request):
    query = request.GET.get('q')
    domain = request.GET.get('domain')
    fournisseurs = Fournisseur.objects.filter(is_active=True).order_by('-note_qualite', 'statut')
    
    if query:
        fournisseurs = fournisseurs.filter(Q(raison_sociale__icontains=query) | Q(code__icontains=query))
    if domain:
        fournisseurs = fournisseurs.filter(domaines__id=domain)
        
    return render(request, 'suppliers/fournisseur_list.html', {'fournisseurs': fournisseurs})

@login_required
def fournisseur_detail(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    return render(request, 'suppliers/fournisseur_detail.html', {'fournisseur': fournisseur})

@login_required
def fournisseur_create(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save(commit=False)
            fournisseur.created_by = request.user
            fournisseur.save()
            form.save_m2m()
            messages.success(request, "Fournisseur créé avec succès.")
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm()
    return render(request, 'suppliers/fournisseur_form.html', {'form': form})

@login_required
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur mis à jour avec succès.")
            return redirect('fournisseur_detail', pk=pk)
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'suppliers/fournisseur_form.html', {'form': form})

@login_required
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    fournisseur.is_active = False
    fournisseur.save()
    messages.warning(request, "Fournisseur archivé.")
    return redirect('fournisseur_list')

# --- Demandes d'Achat ---
@login_required
def demande_achat_list(request):
    demandes = DemandeAchat.objects.all().order_by('-created_at')
    return render(request, 'suppliers/demande_achat_list.html', {'demandes': demandes})

@login_required
def demande_achat_create(request):
    if request.method == 'POST':
        form = DemandeAchatForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            messages.success(request, "Demande d'achat créée.")
            return redirect('demande_achat_list')
    else:
        form = DemandeAchatForm()
    return render(request, 'suppliers/demande_achat_form.html', {'form': form})

@login_required
def demande_achat_soumettre(request, pk):
    demande = get_object_or_404(DemandeAchat, pk=pk)
    if demande.statut == 'brouillon':
        demande.statut = 'soumise'
        demande.save()
        messages.info(request, "Demande soumise pour approbation.")
    return redirect('demande_achat_list')

@login_required
def demande_achat_approuver(request, pk):
    demande = get_object_or_404(DemandeAchat, pk=pk)
    # Check permissions here (e.g., manager role)
    demande.statut = 'approuvee'
    demande.approuve_par = request.user
    demande.date_approbation = timezone.now()
    demande.save()
    messages.success(request, "Demande approuvée.")
    return redirect('demande_achat_list')

# --- Devis et Comparaison ---
@login_required
def devis_comparaison(request, pk):
    demande = get_object_or_404(DemandeAchat, pk=pk)
    devis = DevisComparaison.objects.filter(demande=demande)
    
    if request.method == 'POST':
        devis_id = request.POST.get('retenu_id')
        DevisComparaison.objects.filter(demande=demande).update(est_retenu=False)
        selected_devis = get_object_or_404(DevisComparaison, pk=devis_id)
        selected_devis.est_retenu = True
        selected_devis.save()
        messages.success(request, f"Devis de {selected_devis.fournisseur.raison_sociale} retenu.")
        return redirect('devis_comparaison', pk=pk)
        
    return render(request, 'suppliers/devis_comparaison.html', {'demande': demande, 'devis_list': devis})

@login_required
def devis_create(request, da_pk):
    demande = get_object_or_404(DemandeAchat, pk=da_pk)
    if request.method == 'POST':
        form = DevisComparaisonForm(request.POST, request.FILES)
        if form.is_valid():
            devis = form.save(commit=False)
            devis.demande = demande
            devis.save()
            messages.success(request, "Devis enregistré avec succès.")
            return redirect('devis_comparaison', pk=da_pk)
    else:
        form = DevisComparaisonForm(initial={'demande': demande})
    return render(request, 'suppliers/devis_form.html', {'form': form, 'demande': demande})

# --- Bons de Commande ---
@login_required
def bon_commande_list(request):
    bcs = BonCommande.objects.all().order_by('-date_commande')
    return render(request, 'suppliers/bon_commande_list.html', {'bcs': bcs})

@login_required
def bon_commande_create(request, demande_pk=None):
    demande = get_object_or_404(DemandeAchat, pk=demande_pk) if demande_pk else None
    if request.method == 'POST':
        form = BonCommandeForm(request.POST)
        if form.is_valid():
            bc = form.save(commit=False)
            bc.created_by = request.user
            if demande:
                bc.demande = demande
            bc.save()
            messages.success(request, "Bon de commande créé.")
            return redirect('bon_commande_detail', pk=bc.pk)
    else:
        initial = {}
        if demande:
            retenu = DevisComparaison.objects.filter(demande=demande, est_retenu=True).first()
            initial = {
                'demande': demande,
                'fournisseur': retenu.fournisseur if retenu else None,
                'projet': demande.projet,
                'montant_ht_dzd': retenu.montant_ht_dzd if retenu else demande.montant_estime_dzd,
            }
        form = BonCommandeForm(initial=initial)
    return render(request, 'suppliers/bon_commande_form.html', {'form': form, 'demande': demande})

@login_required
def bon_commande_detail(request, pk):
    bc = get_object_or_404(BonCommande, pk=pk)
    return render(request, 'suppliers/bon_commande_detail.html', {'bc': bc})

@login_required
def bon_commande_valider(request, pk):
    bc = get_object_or_404(BonCommande, pk=pk)
    role_requis = verifier_seuil_approbation(bc.montant_ttc_dzd)
    
    # Règle des 3 devis (obligatoire > 200 000 DZD)
    if bc.montant_ht_dzd > 200000:
        nb_devis = DevisComparaison.objects.filter(demande=bc.demande).count()
        if nb_devis < 3:
            messages.error(request, "Conformité : 3 devis minimum sont requis pour tout achat supérieur à 200 000 DZD.")
            return redirect('bon_commande_detail', pk=pk)

    # Simple check for demo
    if "DG" in role_requis and not (request.user.is_superuser or request.user.groups.filter(name='dg').exists()):
        messages.error(request, f"Seul le DG peut approuver ce montant (> 500k DZD). Rôle requis : {role_requis}")
    else:
        bc.statut = 'confirme'
        bc.approuve_par = request.user
        bc.save()
        # Generate PDF
        pdf_path = generer_pdf_bon_commande(bc)
        bc.pdf_file = pdf_path
        bc.save()
        messages.success(request, "Bon de commande confirmé et PDF généré.")
        
    return redirect('bon_commande_detail', pk=pk)

# --- Factures ---
@login_required
def facture_list(request):
    factures = FactureFournisseur.objects.all().order_by('-date_facture')
    return render(request, 'suppliers/facture_list.html', {'factures': factures})

@login_required
def facture_create(request):
    if request.method == 'POST':
        form = FactureFournisseurForm(request.POST, request.FILES)
        if form.is_valid():
            facture = form.save(commit=False)
            facture.created_by = request.user
            facture.save()
            messages.success(request, "Facture enregistrée.")
            return redirect('facture_list')
    else:
        form = FactureFournisseurForm()
    return render(request, 'suppliers/facture_form.html', {'form': form})
