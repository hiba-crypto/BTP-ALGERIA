import json
from django.utils.deprecation import MiddlewareMixin
from .utils import log_action

class AuditMiddleware(MiddlewareMixin):
    """
    Intercepte toutes les requêtes POST, PUT, DELETE pour l'audit automatique.
    """
    def process_request(self, request):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Capture the request body safely
            try:
                if request.content_type == 'application/json':
                    request._audit_body = json.loads(request.body)
                else:
                    request._audit_body = dict(request.POST)
            except:
                request._audit_body = {}

    def process_response(self, request, response):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Skip login/logout as they are handled in views/signals
            if request.path in ['/accounts/login/', '/accounts/logout/']:
                return response
                
            action = request.method
            status = 'success' if response.status_code < 400 else 'failed'
            module = request.resolver_match.app_name if request.resolver_match else 'unknown'
            
            # Identify if it's an API or standard view
            object_repr = f"Path: {request.path}"
            
            # Simple heuristic for risk level based on URL path or action
            risk_level = 'low'
            if 'delete' in request.path.lower() or request.method == 'DELETE':
                risk_level = 'medium'
            if 'finance' in request.path.lower() or 'salary' in request.path.lower():
                risk_level = 'high'
                
            log_action(
                user=request.user if hasattr(request, 'user') else None,
                action=action,
                module=module,
                object_type='HTTP_REQUEST',
                object_repr=object_repr,
                request=request,
                status=status,
                risk_level=risk_level
            )
            
        return response
