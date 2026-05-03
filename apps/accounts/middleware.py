from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout
import datetime

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_datetime = timezone.now()
            if 'last_activity' in request.session:
                last_activity_str = request.session['last_activity']
                last_activity = datetime.datetime.fromisoformat(last_activity_str)
                timeout_seconds = getattr(settings, 'SESSION_COOKIE_AGE', 1800)
                
                if (current_datetime - last_activity).total_seconds() > timeout_seconds:
                    logout(request)
                    # We might want to add a message here
            
            request.session['last_activity'] = current_datetime.isoformat()
            
        response = self.get_response(request)
        return response

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-XSS-Protection'] = '1; mode=block'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net;"
        return response
