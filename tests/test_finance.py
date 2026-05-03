from django.test import TestCase
from apps.finance.utils import calculer_tva, calculer_tap, calculer_ibs
from decimal import Decimal

class FinanceCalculationTest(TestCase):
    def test_tva_calculation_19_percent(self):
        tva, ttc = calculer_tva(Decimal('100.00'), Decimal('19.00'))
        self.assertEqual(tva, Decimal('19.00'))
        self.assertEqual(ttc, Decimal('119.00'))

    def test_tap_calculation(self):
        tap = calculer_tap(Decimal('1000000.00'))
        self.assertEqual(tap, Decimal('20000.00')) # 2%

    def test_ibs_calculation(self):
        ibs = calculer_ibs(Decimal('1000000.00'))
        self.assertEqual(ibs, Decimal('260000.00')) # 26%

    def test_amounts_are_decimal(self):
        tva, ttc = calculer_tva(Decimal('10.55'), 19)
        self.assertIsInstance(tva, Decimal)
        self.assertIsInstance(ttc, Decimal)
