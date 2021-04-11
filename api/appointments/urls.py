from django.urls import path
from .views import appointment_token, appointment

urlpatterns = [
    path('appt_token/', appointment_token),
    path('', appointment)
]
