from django.test import TestCase
from apps.suppliers.models import Fournisseur, BonCommande
from apps.suppliers.utils import verifier_seuil_approbation
from decimal import Decimal

class ProcurementTest(TestCase):
    def test_purchase_order_requires_dg_above_8M(self):
        role_requis = verifier_seuil_approbation(Decimal('8500000.00'))
        self.assertEqual(role_requis, "DG")

    def test_purchase_order_responsable_below_8M(self):
        role_requis = verifier_seuil_approbation(Decimal('5000000.00'))
        self.assertEqual(role_requis, "Responsable Achats")

    def test_tva_calculation_bc(self):
        bc = BonCommande(
            montant_ht_dzd=Decimal('100000.00'),
            taux_tva=Decimal('19.00')
        )
        bc.save()
        self.assertEqual(bc.montant_tva_dzd, Decimal('19000.00'))
        self.assertEqual(bc.montant_ttc_dzd, Decimal('119000.00'))
