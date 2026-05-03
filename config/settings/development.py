from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# Disable field encryption locally for easier debugging if needed, but we keep it here to match prod.
# FIELD_ENCRYPTION_KEY = 'test_key_for_dev_only_12345678901234567890123456789012' 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
