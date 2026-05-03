from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import AuditLog

def send_security_alert(alert_type, details):
    """Envoi d'un email aux administrateurs pour une alerte de sécurité."""
    subject = f"[ALERTE SECURITE BTP ALGERIA] {alert_type}"
    message = f"Une alerte de sécurité a été déclenchée.\n\nType: {alert_type}\nDétails:\n{details}\n\nMerci de vérifier le tableau de bord d'audit."
    
    # Envoi aux admins (définis dans settings ou groupe admin)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [admin[1] for admin in getattr(settings, 'ADMINS', [])],
        fail_silently=True,
    )

def check_brute_force(ip_address, username):
    """3 échecs en 10 min → email admin"""
    ten_mins_ago = timezone.now() - timedelta(minutes=10)
    failed_attempts = AuditLog.objects.filter(
        action='LOGIN_FAIL',
        ip_address=ip_address,
        timestamp__gte=ten_mins_ago
    ).count()
    
    if failed_attempts >= 3:
        send_security_alert(
            "Brute Force Possible",
            f"Plus de 3 échecs de connexion depuis l'IP {ip_address} pour l'utilisateur {username} dans les 10 dernières minutes."
        )

def check_after_hours(user):
    """Accès avant 7h ou après 21h → alerte"""
    current_hour = timezone.now().hour
    if current_hour < 7 or current_hour >= 21:
        send_security_alert(
            "Accès hors heures de bureau",
            f"L'utilisateur {user.username} s'est connecté à {timezone.now().strftime('%H:%M')}."
        )

def check_large_transaction(amount, transaction_id):
    """Montant > 500 000 DZD → alerte"""
    if amount > 500000:
        send_security_alert(
            "Transaction de montant élevé",
            f"Une transaction (ID: {transaction_id}) de {amount} DZD a été initiée."
        )

def check_bulk_export(user, count):
    """Export > 100 enregistrements → alerte"""
    if count > 100:
        send_security_alert(
            "Exportation massive de données",
            f"L'utilisateur {user.username} a exporté {count} enregistrements."
        )

def check_duplicate_payment(supplier_id, amount, date):
    """Même fournisseur + montant + date → alerte"""
    # This requires models from finance which might not be built yet.
    # Stub implementation.
    send_security_alert(
        "Paiement en double possible",
        f"Un paiement de {amount} DZD pour le fournisseur ID {supplier_id} à la date du {date} semble exister en double."
    )
