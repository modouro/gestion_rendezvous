from django.urls import path, include
from .views import (
    home, register, login_view, 
    logout_view, dashboard_view, 
    list_patients, add_patient, 
    detail_patient, mon_compte, list_rendezvous,
    add_rendezvous, detail_rendezvous, mark_notification_as_read, notifications_view
)

from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RendezVousViewSet, PatientViewSet
    
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'api/patient', PatientViewSet)
router.register(r'api/rendezvous', RendezVousViewSet)


urlpatterns = [
    path('', home, name='index'),  # URL pour la page d'index
    path('dashboard/', dashboard_view, name='dashboard'),  # URL pour le dashboard
    # path('users/', views.list_users, name='list_users'),
    path('users/add/', register, name='register'),
    path('patients/', list_patients, name='list_patients'),
    path('patients/add/', add_patient, name='add_patient'),
    path('patient/<int:patient_pk>/', detail_patient, name='detail_patient'),
    path('compte/', mon_compte, name='compte'),
    path('rendezvous/', list_rendezvous, name='lesrendezvous'),
    path('rendezvous/add/', add_rendezvous, name='add_rendezvous'),
    path('rendezvous/<int:id_rendezvous>/', detail_rendezvous, name='detail_rendezvous'),
    path('notifications/', notifications_view, name='list_notifications'),
    path('mark_notification/', mark_notification_as_read, name='mark_notification_as_read'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'), 
    path('api/', include(router.urls)),
    ]

