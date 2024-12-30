
""" @login_required(login_url="login")
def mon_compte(request):
    # Retrieve the logged-in user
    user = request.user

     # Check if the user is authenticated
    if not user.is_authenticated:
        return redirect('login')  # Redirect unauthenticated users to the login page
    
    try:
        #patient = Patient.objects.get(email=user.email)  Assuming each user has an associated Patient model
        patient = Patient.objects.get(user=user)
    except Patient.DoesNotExist:
        patient = None  # If there's no linked Patient, handle accordingly

    if request.method == 'POST':
        # Update fields
        user.first_name = request.POST.get('prenom', user.first_name)
        user.last_name = request.POST.get('nom', user.last_name)
        user.email = request.POST.get('email', user.email)

        # Update additional fields in the Patient model if applicable
        if patient:
            patient.adresse = request.POST.get('adresse', patient.adresse)
            patient.telephone = request.POST.get('telephone', patient.telephone)
            patient.fonction = request.POST.get('fonction', patient.fonction)
            patient.save()
        
        # Save the User instance
        user.save()

        messages.success(request, "Votre compte a été mis à jour avec succès.")
        return redirect('dashboard')  # Redirect to a desired page after updating

    # Pass the user and patient details to the template
    context = {
        'prenom': user.first_name,
        'nom': user.last_name,
        'email': user.email,
        'patient': patient,  # Pass patient instance if additional fields
        'adresse': patient.adresse if patient else '',
        'telephone': patient.telephone if patient else '',
        'fonction': patient.fonction if patient else '',
    }
    return render(request, "patients/mon_compte.html" , context) """
# 1. Vue DRF pour marquer les notifications comme lues
# Créez une vue DRF pour mettre à jour les notifications de l'utilisateur connecté.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification

class MarkNotificationsAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Marquer toutes les notifications comme lues."""
        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)
        notifications.update(is_read=True)
        return Response({'success': True, 'message': 'Toutes les notifications ont été marquées comme lues.'})
    
# 2. URL de la vue
# Ajoutez l'URL correspondante pour cette vue dans vos urls.py :

# python
# Copier le code
from django.urls import path
from .views import MarkNotificationsAsRead

urlpatterns = [
    path('notifications/mark-as-read/', MarkNotificationsAsRead.as_view(), name='mark_notifications_as_read'),
]
# 3. Modifiez la logique d'affichage dans le template
# Vous allez utiliser Django pour gérer la logique directement dans le template. Par exemple, si l'utilisateur clique sur l'icône, une requête est envoyée au backend pour marquer les notifications comme lues.

# Voici un exemple à inclure dans votre base.html :

# # html
# # Copier le code
   
