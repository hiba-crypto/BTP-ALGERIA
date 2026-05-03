from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField

class CompteComptable(models.Model):
    TYPE_COMPTE_CHOICES = (
        ('actif', 'Actif'),
        ('passif', 'Passif'),
        ('charge', 'Charge'),
        ('produit', 'Produit'),
        ('mixte', 'Mixte'),
    )
    numero = models.CharField(max_length=10, unique=True)
    intitule = models.CharField(max_length=200)
    classe = models.PositiveIntegerField()
    type_compte = models.CharField(max_length=20, choices=TYPE_COMPTE_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.numero} - {self.intitule}"

class EcritureComptable(models.Model):
    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('valide', 'Validée'),
        ('lettree', 'Lettrée'),
    )
    reference = models.CharField(max_length=50, unique=True)
    date_ecriture = models.DateField()
    libelle = models.CharField(max_length=300)
    compte_debit = models.ForeignKey(CompteComptable, on_delete=models.RESTRICT, related_name='debits')
    compte_credit = models.ForeignKey(CompteComptable, on_delete=models.RESTRICT, related_name='credits')
    montant_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    projet = models.ForeignKey('projects.Projet', on_delete=models.SET_NULL, null=True, blank=True)
    piece_justificative = models.FileField(upload_to='finance/pieces/', null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.reference

class CompteBancaire(models.Model):
    BANQUE_CHOICES = (
        ('CPA', 'CPA'),
        ('BEA', 'BEA'),
        ('BNA', 'BNA'),
        ('BADR', 'BADR'),
        ('BDL', 'BDL'),
        ('Societe_Generale_DZ', 'Société Générale Algérie'),
        ('CCP_Algerie_Poste', 'CCP Algérie Poste'),
    )
    banque = models.CharField(max_length=50, choices=BANQUE_CHOICES)
    intitule = models.CharField(max_length=200)
    numero_compte = EncryptedCharField(max_length=255)
    rib = EncryptedCharField(max_length=255)
    solde_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    devise = models.CharField(max_length=10, default='DZD')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.banque} - {self.intitule}"

class MouvementBancaire(models.Model):
    compte = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, related_name='mouvements')
    date_valeur = models.DateField()
    libelle = models.CharField(max_length=300)
    montant_debit_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_credit_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    solde_apres_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    reference_operation = models.CharField(max_length=100, blank=True)
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL, null=True, blank=True)
    rapproche = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date_valeur} - {self.libelle}"
