import json
from .models import AuditLog

def log_action(user, action, module, object_type='', object_id='', object_repr='', 
               old_val=None, new_val=None, request=None, status='success', risk_level='low'):
    """
    Fonction centrale appelée partout dans le projet pour historiser les actions.
    """
    ip_address = None
    user_agent = ''
    session_key = ''
    username = ''

    if request:
        # X-Forwarded-For if behind Nginx/Proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        session_key = request.session.session_key or ''

    if user and user.is_authenticated:
        username = user.username
    elif request and request.POST.get('username'):
        username = request.POST.get('username')

    # Convert dictionaries to JSON strings for EncryptedTextField
    if isinstance(old_val, dict):
        old_val = json.dumps(old_val)
    if isinstance(new_val, dict):
        new_val = json.dumps(new_val)

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        username_snapshot=username,
        ip_address=ip_address,
        user_agent=user_agent,
        session_key=session_key,
        action=action,
        module=module,
        object_type=object_type,
        object_id=str(object_id)[:100],
        object_repr=str(object_repr)[:500],
        old_value=old_val,
        new_value=new_val,
        status=status,
        risk_level=risk_level
    )
