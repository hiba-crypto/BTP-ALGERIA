from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .utils import log_action
from .middleware import get_current_user
import threading

# Modules mapping
MODEL_MODULES = {
    'Projet': 'chef_projet',
    'SituationTravaux': 'chef_projet',
    'Employe': 'rh',
    'Conge': 'rh',
    'BulletinPaie': 'rh',
    'Engin': 'parc',
    'Maintenance': 'parc',
    'AllocationEngin': 'parc',
    'Fournisseur': 'achats',
    'DemandeAchat': 'achats',
    'BonCommande': 'achats',
    'BonReception': 'achats',
    'FactureFournisseur': 'achats',
    'EcritureComptable': 'comptable',
    'CompteBancaire': 'comptable',
    'User': 'admin',
    'UserProfile': 'admin',
    'Role': 'admin',
}

@receiver(post_delete)
def audit_delete(sender, instance, **kwargs):
    model_name = sender.__name__
    if model_name in MODEL_MODULES:
        user = get_current_user()
        # Request is also in thread locals if we want it
        from .middleware import _thread_locals
        request = getattr(_thread_locals, 'request', None)
        
        log_action(
            user=user,
            action='DELETE',
            module=MODEL_MODULES[model_name],
            object_type=model_name,
            object_id=getattr(instance, 'pk', 'N/A'),
            object_repr=str(instance),
            request=request,
            risk_level='medium'
        )

@receiver(post_save)
def audit_create_update(sender, instance, created, **kwargs):
    model_name = sender.__name__
    if model_name in MODEL_MODULES:
        # Avoid double logging for views that already call log_action manually
        # But for "everything else", this is a safety net.
        # Actually, let's only log if not already logged in this request? 
        # For now, let's focus on deletion as requested.
        pass
