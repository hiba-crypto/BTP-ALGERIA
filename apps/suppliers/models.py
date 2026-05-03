from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField
from apps.accounts.models import Wilaya
from django.utils import timezone

class DomaineActivite(models.Model):
    nom = models.CharField(max_length=200)
    
    def __str__(self):
        return self.nom

class Fournisseur(models.Model):
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('blackliste', 'Blacklisté'),
        ('en_validation', 'En Validation'),
        ('inactif', 'Inactif'),
    )
    FORME_JURIDIQUE_CHOICES = (
        ('SARL', 'SARL'),
        ('SPA', 'SPA'),
        ('EURL', 'EURL'),
        ('SNC', 'SNC'),
        ('EI', 'EI'),
        ('Cooperative', 'Coopérative'),
    )
    
    code = models.CharField(max_length=50, unique=True, blank=True)
    raison_sociale = models.CharField(max_length=300)
    forme_juridique = models.CharField(max_length=20, choices=FORME_JURIDIQUE_CHOICES)
    registre_commerce = EncryptedCharField(max_length=255, unique=True)
    nif = EncryptedCharField(max_length=255, unique=True)
    nis = models.CharField(max_length=20)
    article_imposition = models.CharField(max_length=20)
    wilaya = models.ForeignKey(Wilaya, on_delete=models.RESTRICT)
    commune = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    site_web = models.URLField(blank=True)
    domaines = models.ManyToManyField(DomaineActivite)
    delai_moyen_livraison = models.PositiveIntegerField(default=7)
    note_qualite = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_validation')
    motif_blacklist = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fournisseurs_crees')

    def save(self, *args, **kwargs):
        if not self.code:
            from .utils import generer_reference
            self.code = generer_reference('FRN', Fournisseur)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.raison_sociale}"

class DocumentFournisseur(models.Model):
    TYPE_DOC_CHOICES = (
        ('rc', 'Registre de Commerce'),
        ('nif', 'NIF'),
        ('assurance', 'Assurance'),
        ('agrement', 'Agrément'),
        ('autre', 'Autre'),
    )
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='documents')
    type_doc = models.CharField(max_length=20, choices=TYPE_DOC_CHOICES)
    fichier = models.FileField(upload_to='fournisseurs/documents/')
    date_expiration = models.DateField(null=True, blank=True)

class DemandeAchat(models.Model):
    URGENCE_CHOICES = (
        ('normale', 'Normale'),
        ('urgente', 'Urgente'),
        ('tres_urgente', 'Très Urgente'),
    )
    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('soumise', 'Soumise'),
        ('approuvee', 'Approuvée'),
        ('rejetee', 'Rejetée'),
        ('transformee', 'Transformée'),
    )
    reference = models.CharField(max_length=50, unique=True, blank=True)
    objet = models.TextField()
    projet = models.ForeignKey('projects.Projet', on_delete=models.SET_NULL, null=True, blank=True)
    quantite = models.DecimalField(max_digits=10, decimal_places=3)
    unite = models.CharField(max_length=20)
    montant_estime_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    urgence = models.CharField(max_length=20, choices=URGENCE_CHOICES, default='normale')
    justification = models.TextField()
    demandeur = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='demandes_achat')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    approuve_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_approuvees')
    date_approbation = models.DateTimeField(null=True, blank=True)
    motif_rejet = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            from .utils import generer_reference
            self.reference = generer_reference('DA', DemandeAchat)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference

class DevisComparaison(models.Model):
    demande = models.ForeignKey(DemandeAchat, on_delete=models.CASCADE, related_name='devis')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.RESTRICT)
    montant_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=2, default=19.00)
    montant_ttc_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    delai_livraison_jours = models.PositiveIntegerField()
    conditions_paiement = models.TextField()
    fichier_devis = models.FileField(upload_to='achats/devis/')
    est_retenu = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.montant_ttc_dzd = self.montant_ht_dzd * (1 + (self.taux_tva / 100))
        super().save(*args, **kwargs)

class BonCommande(models.Model):
    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('confirme', 'Confirmé'),
        ('livre_partiel', 'Livré Partiel'),
        ('livre_total', 'Livré Total'),
        ('annule', 'Annulé'),
    )
    reference = models.CharField(max_length=50, unique=True, blank=True)
    demande = models.ForeignKey(DemandeAchat, on_delete=models.SET_NULL, null=True, blank=True, related_name='bons_commande')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.RESTRICT)
    projet = models.ForeignKey('projects.Projet', on_delete=models.SET_NULL, null=True, blank=True)
    date_commande = models.DateField(auto_now_add=True)
    date_livraison_prevue = models.DateField()
    montant_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=2, default=19.00)
    montant_tva_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_ttc_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    conditions_paiement = models.TextField()
    lieu_livraison = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    approuve_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bc_approuves')
    pdf_file = models.FileField(upload_to='achats/bons_commande/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bc_crees')

    def save(self, *args, **kwargs):
        if not self.reference:
            from .utils import generer_reference
            self.reference = generer_reference('BC', BonCommande)
        
        # Recalculate totals from lines if possible (handled in signals or manually)
        self.montant_tva_dzd = self.montant_ht_dzd * (Decimal(str(self.taux_tva)) / Decimal('100'))
        self.montant_ttc_dzd = self.montant_ht_dzd + self.montant_tva_dzd
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference

class LigneBonCommande(models.Model):
    bon_commande = models.ForeignKey(BonCommande, on_delete=models.CASCADE, related_name='lignes')
    designation = models.CharField(max_length=300)
    reference_article = models.CharField(max_length=100, blank=True)
    quantite = models.DecimalField(max_digits=10, decimal_places=3)
    unite = models.CharField(max_length=20)
    prix_unitaire_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    montant_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.montant_ht_dzd = self.quantite * self.prix_unitaire_ht_dzd
        super().save(*args, **kwargs)

class BonReception(models.Model):
    STATUT_CHOICES = (
        ('conforme', 'Conforme'),
        ('non_conforme', 'Non Conforme'),
        ('partiel', 'Partiel'),
    )
    reference = models.CharField(max_length=50, unique=True, blank=True)
    bon_commande = models.ForeignKey(BonCommande, on_delete=models.RESTRICT, related_name='bons_reception')
    date_reception = models.DateField()
    receptionnaire = models.ForeignKey(User, on_delete=models.RESTRICT)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    observation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            from .utils import generer_reference
            self.reference = generer_reference('BR', BonReception)
        super().save(*args, **kwargs)

class LigneBonReception(models.Model):
    bon_reception = models.ForeignKey(BonReception, on_delete=models.CASCADE, related_name='lignes')
    ligne_commande = models.ForeignKey(LigneBonCommande, on_delete=models.RESTRICT)
    quantite_commandee = models.DecimalField(max_digits=10, decimal_places=3)
    quantite_recue = models.DecimalField(max_digits=10, decimal_places=3)
    quantite_conforme = models.DecimalField(max_digits=10, decimal_places=3)
    observation = models.CharField(max_length=255, blank=True)

class FactureFournisseur(models.Model):
    STATUT_CHOICES = (
        ('recue', 'Reçue'),
        ('validee', 'Validée'),
        ('payee_partiel', 'Payée Partiel'),
        ('payee_total', 'Payée Total'),
        ('litige', 'Litige'),
    )
    reference = models.CharField(max_length=50, unique=True)
    reference_fournisseur = models.CharField(max_length=100)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.RESTRICT)
    bon_commande = models.ForeignKey(BonCommande, on_delete=models.SET_NULL, null=True, blank=True)
    bon_reception = models.ForeignKey(BonReception, on_delete=models.SET_NULL, null=True, blank=True)
    date_facture = models.DateField()
    date_echeance = models.DateField()
    montant_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=2)
    montant_tva_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    montant_ttc_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    montant_paye_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    solde_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='recue')
    fichier_facture = models.FileField(upload_to='achats/factures/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.montant_tva_dzd = self.montant_ht_dzd * (Decimal(str(self.taux_tva)) / Decimal('100'))
        self.montant_ttc_dzd = self.montant_ht_dzd + self.montant_tva_dzd
        self.solde_dzd = self.montant_ttc_dzd - self.montant_paye_dzd
        super().save(*args, **kwargs)
