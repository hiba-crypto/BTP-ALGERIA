from django.core.management.base import BaseCommand
from apps.audit.models import AuditLog
import pandas as pd
import datetime
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Génère un rapport d\'audit mensuel au format Excel'

    def add_arguments(self, parser):
        parser.add_argument('--month', type=int, default=datetime.datetime.now().month)
        parser.add_argument('--year', type=int, default=datetime.datetime.now().year)

    def handle(self, *args, **options):
        month = options['month']
        year = options['year']
        
        self.stdout.write(f"Génération du rapport d'audit pour {month}/{year}...")
        
        logs = AuditLog.objects.filter(
            timestamp__month=month,
            timestamp__year=year
        )
        
        if not logs.exists():
            self.stdout.write(self.style.WARNING("Aucun log trouvé pour cette période."))
            return

        data = []
        for log in logs:
            data.append({
                'Date': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Utilisateur': log.username_snapshot,
                'IP': log.ip_address,
                'Module': log.module,
                'Action': log.get_action_display(),
                'Objet': log.object_repr,
                'Statut': log.status,
                'Risque': log.get_risk_level_display()
            })
        
        df = pd.DataFrame(data)
        
        filename = f"Rapport_Audit_{year}_{month:02d}.xlsx"
        folder = os.path.join(settings.MEDIA_ROOT, 'reports', 'audit')
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        
        df.to_excel(filepath, index=False)
        
        self.stdout.write(self.style.SUCCESS(f"Rapport généré : {filepath}"))
        
        # In a real task, we would trigger an email send here.
