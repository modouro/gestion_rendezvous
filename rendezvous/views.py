from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from .models import User, Patient, RendezVous, Notification
from django.core.paginator import Paginator
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm, PatientForm, RendezVousForm
from django.db import IntegrityError
from rest_framework import viewsets
from .serializers import(
    UserSerializer, PatientSerializer, RendezVousSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.all()
    serializer_class = RendezVousSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

User = get_user_model()

def home(request):
    # Récupérer les statistiques nécessaires pour l'index
    total_users = User.objects.count()
    total_patients = Patient.objects.count()
    total_rendezvous = RendezVous.objects.count()

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_rendezvous': total_rendezvous,
    }
    return render(request, 'pages/index.html', context)

 
def dashboard_view(request): 
    # Vérifie si l'utilisateur est connecté
    if request.user.is_authenticated:
        total_patients = Patient.objects.filter(user=request.user).count()
    else:
        # Afficher tous les rendez-vous si l'utilisateur n'est pas connecté
        total_patients = Patient.objects.count()

    # Vérifie si l'utilisateur est connecté
    if request.user.is_authenticated:
       total_rendezvous = RendezVous.objects.filter(user=request.user).count() 
    else:
    # Afficher tous les rendez-vous si l'utilisateur n'est pas connecté
        total_rendezvous = RendezVous.objects.count()


    # Vérifie si l'utilisateur est connecté
    if request.user.is_authenticated:
        # Afficher uniquement les rendez-vous de l'utilisateur connecté
        rendezvous_list  = RendezVous.objects.filter(user=request.user).order_by('-date', '-heure')
    else:
        # Afficher tous les rendez-vous si l'utilisateur n'est pas connecté
        rendezvous_list  = RendezVous.objects.all().order_by('-date', '-heure')

    # Nombre de notifications non lues
    unread_notifications_count = request.user.notifications.filter(is_read=False).count() if request.user.is_authenticated else 0
    notifications = request.user.notifications.all() if request.user.is_authenticated else [] 
    return render(request, 'pages/dashboard.html',{
        'total_patients': total_patients,
        'total_rendezvous': total_rendezvous,
        'unread_notifications_count': unread_notifications_count,
        'notifications': notifications,
    })  

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        fonction  = request.POST.get('fonction')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Vérifier si un utilisateur avec cet email existe déjà
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Un utilisateur avec cet existe déjà.')

        else:
            try:
                # Création d'un nouvel utilisateur
                user = User.objects.create_user(
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    fonction = fonction,
                    email=email
                )
                # Sécurisation du mot de passe
                user.set_password(password)
                user.save()
                messages.success(request, 'Votre compte a été crée avec succès !')
                return redirect('login')
            except IntegrityError:
                messages.error(request, "Erreur de création de l'utilisateur. ")
           
    return render(request, 'comptes/register.html') 

#  ---------------------- list_patients -------------------------------
def list_patients(request):
    if request.user.is_authenticated:
        # Vérifie si l'utilisateur est connecté
        patients = Patient.objects.filter(user=request.user).order_by('nom')
    else:
        # Afficher tous les rendez-vous si l'utilisateur n'est pas connecté
        patients = Patient.objects.all().order_by('nom')

    paginator = Paginator(patients, 4)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'patients/mes_patients.html', {
        'page_obj': page_obj,
        'total_rendezvous': RendezVous.objects.count(),
        'total_patients': Patient.objects.count(),
        })
# ---------------------------

# Ajout d'un nouveau patient via un formulaire
@login_required(login_url="login")
def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user  # Associe le patient à l'utilisateur connecté
            patient.save()
            return redirect('list_patients')  # Redirige vers la liste après ajout
    else:
        form = PatientForm()
    return render(request, "patients/ajout_patient.html", {'form': form})

# --------------------------
@login_required(login_url="login")
def detail_patient(request, patient_pk): # C'est une modification en même temps
    patient = get_object_or_404(Patient, pk=patient_pk)

    if request.method == "POST":
        
        form_p = PatientForm(request.POST, instance=patient)
        if form_p.is_valid():
            form_p.save()  # Enregistrer les modifications
            """ messages.success(request, 'Les informations du patient ont été mises à jour avec succès.') """
            return redirect('list_patients')  # Redirige vers la liste des patients
    else:
        form_p = PatientForm(instance=patient)  # Préremplir le formulaire pour l'édition
    
    return render(request, "patients/detail_patient.html", {'form_p': form_p, 'patient': patient})

#  ------------------------------------------------------

@login_required(login_url="login")
def mon_compte(request):
    user = request.user

    # Récupérer le profil Patient pour l'utilisateur connecté
    patient = Patient.objects.filter(user=user).first()
    # patient, created = Patient.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Mise à jour des champs User
        user.first_name = request.POST.get('prenom', user.first_name)
        user.last_name = request.POST.get('nom', user.last_name)
        user.fonction = request.POST.get('fonction', user.fonction)
        user.adresse = request.POST.get('adresse', user.fonction)
        user.telephone = request.POST.get('telephone', user.telephone)
        user.email = request.POST.get('email', user.email)
        
        # Sauvegarder l'utilisateur
        user.save()

        messages.success(request, "Votre compte a été mis à jour avec succès.")
        return redirect('dashboard')

    # Passer les informations au contexte
    context = {
        'nom': user.last_name,
        'fonction': user.fonction,
        'adresse': user.adresse,
        'telephone': user.telephone,
        'email': user.email,
    }

    return render(request, "patients/mon_compte.html", context)

# ----------------------------- les rendez-vous --------------------
# Ajout d'un nouveau rendez-vous via un formulaire
@login_required(login_url="login")
def add_rendezvous(request):
    if request.method == 'POST':
        form = RendezVousForm(request.POST)
        if form.is_valid():
            # Ne pas sauvegarder directement, utiliser commit=False pour modifier l'instance avant de la sauvegarder
            rendezvous = form.save(commit=False)
            rendezvous.user = request.user  # Associer l'utilisateur connecté
            rendezvous.save()  # Sauvegarder l'instance
            messages.success(request, "Rendez-vous ajouté avec succès.")
            return redirect('lesrendezvous')  # Redirection après soumission réussie
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = RendezVousForm()

    # Si vous filtrez les patients par utilisateur, ajoutez un filtre
   # patients = Patient.objects.filter(user=request.user)  # Récupérer uniquement les patients de l'utilisateur connecté
    patients = Patient.objects.all()
    return render(request, 'rendezvous/ajout_rendezvous.html', {
        'form': form, 
        'patients': patients,
        # 'user': request.user,  # Ajouter l'utilisateur connecté
    })
  
# Affiche la liste des rendez-vous ---------------------------
def list_rendezvous(request):
    today = date.today()

    # Vérifie si l'utilisateur est connecté
    if request.user.is_authenticated:
        # Afficher uniquement les rendez-vous de l'utilisateur connecté
        rendezvous_list  = RendezVous.objects.filter(user=request.user).order_by('-date', '-heure')
    else:
        # Afficher tous les rendez-vous si l'utilisateur n'est pas connecté
        rendezvous_list  = RendezVous.objects.all().order_by('-date', '-heure')


    # Pagination - Nombre d'éléments par page
    paginator = Paginator(rendezvous_list, 4)  # 5 rendez-vous par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "rendezvous/mes_rendezvous.html", {
        'search_type': 'rendezvous',
        'page_obj': page_obj,
        'rendezvous_list': rendezvous_list,
        'total_rendezvous': RendezVous.objects.count(),
        'total_patients': Patient.objects.count(),
        'today': today,
        })

#--------------------------------- detail RV ----------------------
@login_required(login_url="login")
def detail_rendezvous(request, id_rendezvous):
    rendezvous = get_object_or_404(RendezVous, id=id_rendezvous, user=request.user)

    # patients   = Patient.objects.all()  # recupére les données des patients
    # Filtrer les patients liés à l'utilisateur connecté
    patients = Patient.objects.filter(user=request.user)

    if request.method == 'POST':  
        form_r = RendezVousForm(request.POST, instance=rendezvous)
        if form_r.is_valid():
            form_r.save()
            return redirect('lesrendezvous')
    else:
        form_r = RendezVousForm(instance=rendezvous)

    return render(request, 'rendezvous/detail_rv.html', {
        'rendezvous': rendezvous, 
        'patients': patients,
        'form_r': form_r,
        }) 
# ---------------------------  notification  -----------------------

def notifications_view(request):
    notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    context = {
        'notifications_count': notifications_count,
    }
    return render(request, 'notification/notification.html', context)

# ----------------------------- vue de mise a jour is read

@login_required
def mark_notification_as_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('dashboard')  # Redirigez vers votre tableau de bord ou une autre page


# --------------------------- connexion ----------------------------
from django.urls import reverse

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Si l'utilisateur est authentifié, le connecter et rediriger
            login(request, user)

            return redirect(reverse('dashboard'))
            #return redirect('dashboard')  # Rediriger vers la page d'accueil
        else:
            # Sinon, afficher un message d'erreur
            messages.error(request, "Identifiants invalides. Veuillez réessayer.")
    return render(request, 'comptes/login.html')
    
# ------------------------------------ Redirection pour la page commencer ------------------

def commencer(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Rediriger vers le tableau de bord si connecté
    return redirect('register')  # Rediriger vers la page d'inscription si non connecté

# ------------------- deconexion ------------------------------------

def logout_view(request):
    logout(request)  # Déconnexion de l'utilisateur
    return redirect('login')  # Redirigez vers la page de connexion
