from django.test import TestCase
from apps.employees.models import Employe, Wilaya, Poste, BulletinPaie
from decimal import Decimal
import datetime

class HRModuleTest(TestCase):
    def setUp(self):
        self.wilaya = Wilaya.objects.create(code='16', nom_fr='Alger', nom_ar='الجزائر')
        self.poste = Poste.objects.create(titre='Ingénieur', categorie='Cadre', salaire_base_min=80000)
        self.employe = Employe.objects.create(
            nom='Berrabah', prenom='Amine',
            matricule='EMP001',
            poste=self.poste,
            date_recrutement=datetime.date(2023, 1, 1),
            wilaya_residence=self.wilaya
        )

    def test_create_employee_with_encrypted_fields(self):
        self.employe.nss = "123456789012"
        self.employe.save()
        # Verify encryption is transparent in the model
        emp = Employe.objects.get(pk=self.employe.pk)
        self.assertEqual(emp.nss, "123456789012")

    def test_payroll_calculation_cnas_9_percent(self):
        bulletin = BulletinPaie(
            employe=self.employe,
            salaire_brut=Decimal('100000.00'),
            mois=5, annee=2024
        )
        bulletin.save()
        self.assertEqual(bulletin.cnas_salariale, Decimal('9000.00'))

    def test_soft_delete_employee(self):
        self.employe.delete()
        self.assertTrue(Employe.all_objects.filter(pk=self.employe.pk).exists())
        self.assertFalse(Employe.objects.filter(pk=self.employe.pk).exists())
