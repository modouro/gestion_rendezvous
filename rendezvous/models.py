from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Modèle utilisateur personnalisé pour étendre les fonctionnalités de base de l'utilisateur
class User(AbstractUser):
    first_name = models.CharField(max_length=250, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    fonction = models.CharField(max_length=255, verbose_name="Fonction")
    adresse = models.CharField(max_length=255, verbose_name="Adresse")
    telephone = models.CharField(max_length=15, verbose_name="Téléphone")
    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")

    REQUIRED_FIELDS = ['first_name', 'last_name', 'fonction', 'adresse', 'telephone']  # Pas besoin de 'username'
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    # Champs hérités d'AbstractUser pour les permissions et les groupes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        verbose_name='user permissions',
    )

class Patient(models.Model): 
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ] 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    age = models.PositiveIntegerField(verbose_name="Âge", default=0)  # Âge du patient (doit être positif)
    adresse = models.CharField(max_length=255, verbose_name="Adresse")
    telephone = models.CharField(max_length=15, unique=True, verbose_name="Téléphone")

    def __str__(self):
        return f"{self.prenom} {self.nom}"
       
    def clean(self):
        super().clean()
        if self.age <= 0:
            raise ValidationError("L'âge doit être un nombre positif.")


# Modèle Rendez-vous
class RendezVous(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rendezvous", verbose_name="Utilisateur")
    titre = models.CharField(max_length=100, verbose_name="Titre du rendez-vous")  # Titre du rendez-vous
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Patient", related_name="rendezvous")
    date = models.DateField(verbose_name="Date du rendez-vous")  # Date du rendez-vous
    heure = models.TimeField(verbose_name="Heure du rendez-vous")  # Heure du rendez-vous
    lieu = models.CharField(max_length=255, verbose_name="Lieu du rendez-vous")  # Lieu du rendez-vous

    class Meta:
        unique_together = ('patient', 'date', 'heure')  # Empêche les doublons Si un rendez-vous ne peut pas 
                                                        #  avoir le même  titre, patient, date et heure, vous 
                                                        #  pouvez ajouter une contrainte unique.        

    def __str__(self):
        return f"{self.titre} avec {self.patient.prenom} {self.patient.nom} le {self.date} à {self.heure}"

#  Modele Notification 
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    #created_at = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"