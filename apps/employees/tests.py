from django.test import TestCase
from decimal import Decimal
from .models import Employe, Poste, BulletinPaie
from .utils import calculer_bulletin
from apps.accounts.models import Wilaya
import datetime

class PayrollTestCase(TestCase):
    def setUp(self):
        # Create base data
        self.wilaya = Wilaya.objects.create(code="16", nom_fr="Alger", nom_ar="الجزائر")
        self.poste = Poste.objects.create(
            titre="Ingénieur",
            categorie="Cadre",
            coefficient=100,
            salaire_base_min=50000,
            salaire_base_max=100000
        )
        self.employe = Employe.objects.create(
            matricule="EMP001",
            nom="Benali",
            prenom="Kamel",
            date_naissance=datetime.date(1985, 1, 1),
            wilaya_naissance=self.wilaya,
            date_embauche=datetime.date(2020, 1, 1),
            type_contrat="CDI",
            poste=self.poste,
            wilaya_travail=self.wilaya,
            salaire_base=Decimal('60000'),
            mode_paiement="virement_cpa"
        )

    def test_payroll_calculation(self):
        """Test if CNAS and CACOBATPH are correctly calculated."""
        calc = calculer_bulletin(self.employe, 5, 2026)
        
        # CNAS Salariale = 9% of Brut
        # Brut here = 60000 + Ancienneté (6 years = 6%) = 63600
        expected_brut = Decimal('63600')
        self.assertEqual(calc['salaire_brut'], expected_brut)
        
        expected_cnas = expected_brut * Decimal('0.09')
        self.assertEqual(calc['cnas'], expected_cnas)
        
        # CACOBATPH = 3% of Brut
        expected_cacobatph = expected_brut * Decimal('0.03')
        self.assertEqual(calc['cacobatph'], expected_cacobatph)
        
        # Verify Net is correct
        self.assertTrue(calc['salaire_net'] < calc['salaire_brut'])

    def test_irg_is_progressive(self):
        """Test if IRG is 0 for low salaries and positive for high salaries."""
        # Lower salary
        self.employe.salaire_base = Decimal('25000')
        calc = calculer_bulletin(self.employe, 5, 2026)
        # 25000 + 1500 (anc) = 26500. CNAS = 2385. Taxable = 24115. IRG should be 0 (< 30k)
        self.assertEqual(calc['irg'], Decimal('0'))
        
        # Higher salary
        self.employe.salaire_base = Decimal('100000')
        calc = calculer_bulletin(self.employe, 5, 2026)
        self.assertTrue(calc['irg'] > 0)
