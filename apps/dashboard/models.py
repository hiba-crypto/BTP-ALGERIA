from django.db import models

class PublicQuoteRequest(models.Model):
    nom_complet = models.CharField(max_length=200)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_traite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom_complet} - {self.sujet}"
