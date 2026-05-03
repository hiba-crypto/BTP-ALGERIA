import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('btp_algeria')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Backup quotidien 03:00
    'backup-db-daily': {
        'task': 'apps.audit.tasks.backup_postgresql',
        'schedule': crontab(hour=3, minute=0),
    },
    # Alertes flotte 08:00
    'alertes-flotte-daily': {
        'task': 'apps.fleet.tasks.verifier_echeances_flotte',
        'schedule': crontab(hour=8, minute=0),
    },
    # Alertes RH 08:00
    'alertes-rh-daily': {
        'task': 'apps.employees.tasks.verifier_alertes_rh',
        'schedule': crontab(hour=8, minute=0),
    },
    # Bulletins de paie 1er du mois 06:00
    'generer-bulletins-mensuels': {
        'task': 'apps.employees.tasks.generer_bulletins_mensuels',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),
    },
    # Rapport audit 1er du mois 07:00
    'rapport-audit-mensuel': {
        'task': 'apps.audit.tasks.envoyer_rapport_audit_mensuel',
        'schedule': crontab(day_of_month=1, hour=7, minute=0),
    },
}
