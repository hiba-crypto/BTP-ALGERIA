from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField
from decimal import Decimal

class TypeEngin(models.Model):
    nom = models.CharField(max_length=100)
    consommation_ref_lh = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return self.nom

class Engin(models.Model):
    ETAT_CHOICES = (
        ('en_service', 'En Service'),
        ('en_maintenance', 'En Maintenance'),
        ('hs', 'Hors Service'),
        ('loue', 'Loué'),
        ('vendu', 'Vendu'),
        ('au_depot', 'Au Dépôt'),
    )
    code = models.CharField(max_length=50, unique=True, blank=True)
    designation = models.CharField(max_length=300)
    type_engin = models.ForeignKey(TypeEngin, on_delete=models.RESTRICT)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)
    immatriculation = models.CharField(max_length=20, blank=True)
    annee_fabrication = models.PositiveIntegerField()
    annee_mise_en_service = models.PositiveIntegerField()
    valeur_achat_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    taux_amortissement_annuel = models.DecimalField(max_digits=5, decimal_places=2)
    valeur_residuelle_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    taux_location_journalier_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    projet_actuel = models.ForeignKey('projects.Projet', on_delete=models.SET_NULL, null=True, blank=True)
    date_affectation = models.DateField(null=True, blank=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='au_depot')
    compteur_heures = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    compteur_km = models.PositiveIntegerField(default=0)
    prochain_ct_date = models.DateField(null=True, blank=True)
    expiration_assurance = models.DateField(null=True, blank=True)
    consommation_moyenne_lh = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    photo = models.ImageField(upload_to='fleet/photos/', null=True, blank=True)
    carte_grise = models.FileField(upload_to='fleet/docs/', null=True, blank=True)
    police_assurance = models.FileField(upload_to='fleet/docs/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.code:
            import datetime
            count = Engin.objects.count() + 1
            self.code = f"ENG-{count:04d}"
        
        from datetime import date
        years_diff = date.today().year - self.annee_mise_en_service
        depreciation = (Decimal(str(self.valeur_achat_dzd)) * (Decimal(str(self.taux_amortissement_annuel)) / Decimal('100'))) * Decimal(str(years_diff))
        self.valeur_residuelle_dzd = max(Decimal('0'), Decimal(str(self.valeur_achat_dzd)) - depreciation)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.designation}"

class AllocationEngin(models.Model):
    engin = models.ForeignKey(Engin, on_delete=models.CASCADE, related_name='allocations')
    projet = models.ForeignKey('projects.Projet', on_delete=models.CASCADE, related_name='allocations_engins')
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    heures_travaillees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taux_journalier_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    cout_total_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.date_fin and self.date_debut:
            days = (self.date_fin - self.date_debut).days + 1
            self.cout_total_dzd = Decimal(str(days)) * self.taux_journalier_dzd
        else:
            self.cout_total_dzd = 0
        super().save(*args, **kwargs)

class Maintenance(models.Model):
    TYPE_CHOICES = (
        ('preventive', 'Préventive'),
        ('corrective', 'Corrective'),
        ('controle_technique', 'Contrôle Technique'),
        ('revision_generale', 'Révision Générale'),
    )
    STATUT_CHOICES = (
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En Cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    )
    reference = models.CharField(max_length=50, unique=True, blank=True)
    engin = models.ForeignKey(Engin, on_delete=models.CASCADE, related_name='maintenances')
    type_maintenance = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_entree = models.DateField()
    date_sortie = models.DateField(null=True, blank=True)
    compteur_heures_entree = models.DecimalField(max_digits=10, decimal_places=2)
    description_panne = models.TextField(blank=True)
    travaux_effectues = models.TextField()
    mecanicien = models.ForeignKey('employees.Employe', on_delete=models.SET_NULL, null=True, blank=True)
    prestataire_externe = models.CharField(max_length=200, blank=True)
    cout_main_oeuvre_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cout_pieces_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cout_total_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    prochaine_maintenance_heures = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prochaine_maintenance_date = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            import datetime
            year = datetime.datetime.now().year
            count = Maintenance.objects.filter(reference__startswith=f'MNT-{year}').count() + 1
            self.reference = f"MNT-{year}-{count:04d}"
        self.cout_total_dzd = self.cout_main_oeuvre_dzd + self.cout_pieces_dzd
        super().save(*args, **kwargs)

class PieceDetachee(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='pieces')
    designation = models.CharField(max_length=200)
    reference_piece = models.CharField(max_length=100, blank=True)
    quantite = models.DecimalField(max_digits=8, decimal_places=3)
    prix_unitaire_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    montant_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.montant_dzd = self.quantite * self.prix_unitaire_dzd
        super().save(*args, **kwargs)

class BonCarburant(models.Model):
    TYPE_CARBURANT_CHOICES = (
        ('gasoil', 'Gasoil'),
        ('essence', 'Essence'),
        ('gpl', 'GPL'),
    )
    reference = models.CharField(max_length=50, unique=True, blank=True)
    engin = models.ForeignKey(Engin, on_delete=models.CASCADE, related_name='carburants')
    projet = models.ForeignKey('projects.Projet', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    type_carburant = models.CharField(max_length=20, choices=TYPE_CARBURANT_CHOICES)
    quantite_litres = models.DecimalField(max_digits=8, decimal_places=2)
    prix_litre_dzd = models.DecimalField(max_digits=8, decimal_places=2)
    montant_dzd = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    station_service = models.CharField(max_length=200)
    compteur_heures = models.DecimalField(max_digits=10, decimal_places=2)
    conducteur = models.ForeignKey('employees.Employe', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            import datetime
            year = datetime.datetime.now().year
            count = BonCarburant.objects.filter(reference__startswith=f'CAR-{year}').count() + 1
            self.reference = f"CAR-{year}-{count:04d}"
        self.montant_dzd = self.quantite_litres * self.prix_litre_dzd
        super().save(*args, **kwargs)
