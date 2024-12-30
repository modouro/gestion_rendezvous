from django import forms
from .models import User, Patient, RendezVous
from datetime import date, time
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        min_length=8,
        help_text="Le mot de passe doit comporter au moins 8 caractères."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'fonction', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d’utilisateur'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fonction'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse e-mail'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hachage du mot de passe
        if commit:
            user.save()
        return user

    
# ----------------  fin du formulaire ----------------

# Formulaire pour le modèle Patient
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['prenom', 'nom', 'sexe', 'age', 'adresse', 'telephone']
        widgets = {
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}, choices=Patient.SEXE_CHOICES),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Âge'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
        }

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if not telephone.isdigit():
            raise forms.ValidationError("Le numéro de téléphone doit contenir uniquement des chiffres.")
        if len(telephone) < 9 or len(telephone) > 15:
            raise forms.ValidationError("Le numéro de téléphone doit contenir entre 10 et 15 chiffres.")
        return telephone
    
# ------------------------------  de revoir --------------------------------

# Formulaire pour le modèle RendezVous
class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['titre', 'patient', 'date', 'heure', 'lieu']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du rendez-vous'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date', 'type': 'date'}),
            'heure': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Heure', 'type': 'time'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Définir la date minimale à aujourd'hui pour empêcher la sélection de dates passées
        self.fields['date'].widget.attrs['min'] = date.today().isoformat()

    # ------------- Vérifier la date des rendez-vous, -----------------------------
    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        
        # Vérifiez si la date est un week-end (samedi = 5, dimanche = 6)
        if selected_date.weekday() in (5, 6): # c'est le comptage des dates commence par 0
            raise forms.ValidationError("Les rendez-vous ne peuvent pas être fixés un samedi ou un dimanche.")
        
        # Vérifiez également que la date n'est pas dans le passé
        if selected_date < date.today():
            raise forms.ValidationError("La date du rendez-vous ne peut pas être dans le passé.")
        
        return selected_date
    
    # ------------- Vérifier l'heure des rendez-vous, ils doivent être entre 08 et 18 heures --------------
    def clean(self):
        cleaned_data = super().clean()
        heure = cleaned_data.get('heure')
        if heure:
            # Vérification que l'heure est entre 08:00 et 18:00
            if not time(7, 30) <= heure <= time(18, 30):
                raise ValidationError("L'heure du rendez-vous doit être entre 08:00 et 18:00.")

        # Retourne les données nettoyées si tout est valide
        return cleaned_data
