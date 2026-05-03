from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
from decimal import Decimal
from apps.accounts.models import Wilaya

class Poste(models.Model):
    CATEGORIE_CHOICES = (
        ('Ouvrier', 'Ouvrier'),
        ('Technicien', 'Technicien'),
        ('Maitrise', 'Agent de Maîtrise'),
        ('Cadre', 'Cadre'),
        ('Cadre_sup', 'Cadre Supérieur'),
    )
    titre = models.CharField(max_length=200)
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)
    coefficient = models.PositiveIntegerField()
    salaire_base_min = models.DecimalField(max_digits=15, decimal_places=2)
    salaire_base_max = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.titre

class Employe(models.Model):
    SITUATION_FAM_CHOICES = (
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
    )
    CONTRAT_CHOICES = (
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Interim', 'Intérim'),
        ('Stage', 'Stage'),
        ('Apprentissage', 'Apprentissage'),
    )
    PAIEMENT_CHOICES = (
        ('virement_cpa', 'Virement CPA'),
        ('virement_bea', 'Virement BEA'),
        ('virement_bna', 'Virement BNA'),
        ('cheque', 'Chèque'),
        ('especes', 'Espèces'),
    )
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('conge', 'En Congé'),
        ('suspendu', 'Suspendu'),
        ('demissionne', 'Démissionné'),
        ('licencie', 'Licencié'),
        ('retraite', 'Retraité'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employe_profile', null=True, blank=True)
    matricule = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    nom_arabe = models.CharField(max_length=200, blank=True)
    date_naissance = models.DateField()
    wilaya_naissance = models.ForeignKey(Wilaya, on_delete=models.RESTRICT, related_name='employes_nes')
    commune_naissance = models.CharField(max_length=100)
    
    cni = EncryptedCharField(max_length=50, unique=True)
    num_cnas = EncryptedCharField(max_length=50)
    nif_fiscal = EncryptedCharField(max_length=50)
    adresse = EncryptedTextField()
    telephone = EncryptedCharField(max_length=50)
    rib_bancaire = EncryptedCharField(max_length=100)
    
    email_pro = models.EmailField(unique=True, blank=True, null=True)
    situation_familiale = models.CharField(max_length=20, choices=SITUATION_FAM_CHOICES)
    nb_enfants = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='employees/photos/%Y/%m/', null=True, blank=True)
    contact_urgence_nom = EncryptedCharField(max_length=200)
    contact_urgence_tel = EncryptedCharField(max_length=50)
    
    type_contrat = models.CharField(max_length=20, choices=CONTRAT_CHOICES)
    date_embauche = models.DateField()
    date_fin_contrat = models.DateField(null=True, blank=True)
    poste = models.ForeignKey(Poste, on_delete=models.RESTRICT)
    wilaya_travail = models.ForeignKey(Wilaya, on_delete=models.RESTRICT, related_name='employes_wilaya')
    
    # Normally we would use EncryptedDecimalField but django-encrypted-model-fields might not support it directly
    # So we use a CharField and cast it in property, or just assume it is supported if the package allows it.
    # To be safe, we use EncryptedCharField and cast to Decimal.
    salaire_base_crypt = EncryptedCharField(max_length=50)
    
    mode_paiement = models.CharField(max_length=50, choices=PAIEMENT_CHOICES)
    projet_affecte = models.ForeignKey('projects.Projet', on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    @property
    def salaire_base(self):
        from decimal import Decimal
        return Decimal(self.salaire_base_crypt) if self.salaire_base_crypt else Decimal('0')
        
    @salaire_base.setter
    def salaire_base(self, value):
        self.salaire_base_crypt = str(value)

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"

class DocumentEmploye(models.Model):
    TYPE_DOC_CHOICES = (
        ('cni', 'CNI'),
        ('cnas', 'Carte CNAS'),
        ('diplome', 'Diplôme'),
        ('casier', 'Casier Judiciaire'),
        ('residence', 'Certificat de Résidence'),
        ('contrat', 'Contrat de Travail'),
        ('autre', 'Autre'),
    )
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='documents')
    type_doc = models.CharField(max_length=20, choices=TYPE_DOC_CHOICES)
    fichier = models.FileField(upload_to='employees/documents/%Y/%m/')
    date_expiration = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Contrat(models.Model):
    TYPE_CONTRAT_CHOICES = (
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Interim', 'Intérim'),
        ('Stage', 'Stage'),
        ('Apprentissage', 'Apprentissage'),
    )
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='contrats')
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    salaire_base_dzd = models.DecimalField(max_digits=15, decimal_places=2)
    fichier_contrat = models.FileField(upload_to='employees/contrats/', null=True, blank=True)
    statut = models.CharField(max_length=20, choices=[('actif', 'Actif'), ('expire', 'Expiré'), ('annule', 'Annulé')], default='actif')
    created_at = models.DateTimeField(auto_now_add=True)

class Conge(models.Model):
    TYPE_CHOICES = (
        ('annuel', 'Annuel'),
        ('maladie', 'Maladie'),
        ('maternite', 'Maternité'),
        ('paternite', 'Paternité'),
        ('exceptionnel', 'Exceptionnel'),
        ('cacobatph', 'CACOBATPH (BTP)'),
        ('sans_solde', 'Sans Solde'),
    )
    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
    )
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='conges')
    type_conge = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    nb_jours = models.PositiveIntegerField(default=0)
    motif = models.TextField()
    justificatif = models.FileField(upload_to='employees/conges/%Y/%m/', null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    approuve_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.date_debut and self.date_fin:
            self.nb_jours = (self.date_fin - self.date_debut).days + 1
        super().save(*args, **kwargs)

class Presence(models.Model):
    STATUT_CHOICES = (
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('retard', 'Retard'),
        ('mission', 'Mission'),
        ('conge', 'Congé'),
    )
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField()
    projet = models.ForeignKey('projects.Projet', on_delete=models.SET_NULL, null=True, blank=True)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='present')
    heures_sup = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    note = models.TextField(blank=True)

class BulletinPaie(models.Model):
    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('paye', 'Payé'),
    )
    employe = models.ForeignKey(Employe, on_delete=models.RESTRICT, related_name='bulletins')
    mois = models.PositiveIntegerField()
    annee = models.PositiveIntegerField()
    salaire_base = models.DecimalField(max_digits=15, decimal_places=2)
    indemnite_zone = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    prime_rendement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    heures_sup_montant = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    indemnite_repas = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    prime_anciennete = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    autres_primes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    salaire_brut = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cnas_salariale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    irg = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cacobatph_salariale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    retenues_diverses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    salaire_net = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    pdf_file = models.FileField(upload_to='employees/bulletins/%Y/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.salaire_brut = (
            self.salaire_base + self.indemnite_zone + self.prime_rendement + 
            self.heures_sup_montant + self.prime_anciennete + self.autres_primes
        )
        self.cnas_salariale = self.salaire_brut * Decimal('0.09')
        # IRG and net salary should be calculated via utils before save
        super().save(*args, **kwargs)
