from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import AuditLog
from .utils import log_action

# To keep track of old values before save
_local_thread_state = {}

def get_model_dict(instance):
    """Convert model instance to dict, excluding relations for simplicity."""
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields:
        if f.name == 'password':
            continue
        val = getattr(instance, f.attname)
        data[f.name] = val
    return data

@receiver(pre_save)
def capture_old_state(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog' or sender.__name__ == 'Session':
        return
        
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _local_thread_state[id(instance)] = get_model_dict(old_instance)
        except sender.DoesNotExist:
            pass

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    if sender.__name__ == 'AuditLog' or sender.__name__ == 'Session':
        return
        
    action = 'CREATE' if created else 'UPDATE'
    old_val = _local_thread_state.pop(id(instance), None)
    new_val = get_model_dict(instance)
    
    # We don't have request user in signals easily without threadlocals middleware,
    # so we log SYSTEM or rely on middleware. This is a basic implementation.
    log_action(
        user=None,  # Ideal: get from threadlocal middleware
        action=action,
        module=sender._meta.app_label,
        object_type=sender.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        old_val=old_val if not created else None,
        new_val=new_val
    )

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog' or sender.__name__ == 'Session':
        return
        
    old_val = get_model_dict(instance)
    
    log_action(
        user=None,
        action='DELETE',
        module=sender._meta.app_label,
        object_type=sender.__name__,
        object_id=instance.pk,
        object_repr=str(instance),
        old_val=old_val,
        risk_level='medium'
    )
