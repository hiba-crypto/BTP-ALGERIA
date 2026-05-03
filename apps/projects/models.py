from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

class Client(models.Model):
    TYPE_CHOICES = (
        ('commune', 'Commune'),
        ('daira', 'Daïra'),
        ('wilaya', 'Wilaya'),
        ('ministere', 'Ministère'),
        ('prive', 'Privé'),
        ('etranger', 'Étranger'),
    )
    nom = models.CharField(max_length=300)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    wilaya = models.ForeignKey('accounts.Wilaya', on_delete=models.RESTRICT)
    contact_nom = models.CharField(max_length=150)
    contact_tel = models.CharField(max_length=20)
    contact_email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Projet(models.Model):
    TYPE_TRAVAUX_CHOICES = (
        ('batiment', 'Bâtiment'),
        ('tp', 'Travaux Publics'),
        ('hydraulique', 'Hydraulique'),
        ('vrd', 'VRD'),
        ('renovation', 'Rénovation'),
        ('amenagement', 'Aménagement'),
    )
    STATUT_CHOICES = (
        ('etude', 'Étude'),
        ('preparation', 'Préparation'),
        ('en_cours', 'En cours'),
        ('arret', 'À l\'arrêt'),
        ('reception_provisoire', 'Réception provisoire'),
        ('reception_definitive', 'Réception définitive'),
        ('clos', 'Clos'),
        ('litige', 'En litige'),
        ('resilie', 'Résilié'),
    )
    reference = models.CharField(max_length=50, unique=True)
    intitule = models.CharField(max_length=500)
    intitule_arabe = models.CharField(max_length=500, blank=True)
    reference_marche = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(Client, on_delete=models.RESTRICT)
    type_travaux = models.CharField(max_length=50, choices=TYPE_TRAVAUX_CHOICES)
    wilaya_chantier = models.ForeignKey('accounts.Wilaya', on_delete=models.RESTRICT)
    commune_chantier = models.CharField(max_length=100)
    adresse_chantier = models.TextField(blank=True)
    montant_marche_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=2, choices=[(9.00, '9%'), (19.00, '19%')], default=19.00)
    montant_marche_ttc_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_ordre_service = models.DateField()
    delai_execution_jours = models.PositiveIntegerField()
    date_fin_contractuelle = models.DateField(blank=True, null=True)
    date_fin_reelle_prevue = models.DateField(null=True, blank=True)
    avancement_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    budget_previsionnel_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    chef_projet = models.ForeignKey('employees.Employe', related_name='projets_chef', on_delete=models.RESTRICT, null=True, blank=True)
    conducteur_travaux = models.ForeignKey('employees.Employe', on_delete=models.RESTRICT, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='etude')
    taux_penalite_retard = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0003'))
    garantie_bonne_fin_pct = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('5.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.montant_marche_ttc_dzd = self.montant_marche_ht_dzd * (Decimal('1') + (Decimal(str(self.taux_tva)) / Decimal('100')))
        if self.date_ordre_service and self.delai_execution_jours:
            from datetime import timedelta
            self.date_fin_contractuelle = self.date_ordre_service + timedelta(days=self.delai_execution_jours)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.intitule[:50]}"

class SituationTravaux(models.Model):
    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('soumise', 'Soumise'),
        ('validee', 'Validée'),
        ('payee', 'Payée'),
    )
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='situations')
    numero = models.PositiveIntegerField()
    mois = models.PositiveIntegerField()
    annee = models.PositiveIntegerField()
    montant_cumul_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    montant_periode_ht_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    avance_demarrage_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    retenue_garantie_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    net_a_facturer_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    tva_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    net_ttc_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_soumission = models.DateField(null=True, blank=True)
    date_paiement = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.retenue_garantie_dzd = self.montant_periode_ht_dzd * (self.projet.garantie_bonne_fin_pct / Decimal('100'))
        self.net_a_facturer_dzd = self.montant_periode_ht_dzd - self.avance_demarrage_dzd - self.retenue_garantie_dzd
        self.tva_dzd = self.net_a_facturer_dzd * (Decimal(str(self.projet.taux_tva)) / Decimal('100'))
        self.net_ttc_dzd = self.net_a_facturer_dzd + self.tva_dzd
        super().save(*args, **kwargs)

class RentabiliteProjet(models.Model):
    projet = models.OneToOneField(Projet, on_delete=models.CASCADE, related_name='rentabilite')
    ca_realise_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cout_mo_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cout_materiaux_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cout_engins_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cout_sous_traitance_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    frais_generaux_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    marge_brute_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    marge_brute_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    marge_nette_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    marge_nette_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    retard_jours = models.IntegerField(default=0)
    penalites_dzd = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    derniere_maj = models.DateTimeField(auto_now=True)

    @property
    def couts_totaux_dzd(self):
        return self.cout_mo_dzd + self.cout_materiaux_dzd + self.cout_engins_dzd + self.cout_sous_traitance_dzd

@receiver(post_save, sender=Projet)
def create_rentabilite(sender, instance, created, **kwargs):
    if created:
        RentabiliteProjet.objects.create(projet=instance)
