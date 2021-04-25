from django.urls import path
from .views import appointment_token, appointment, appointment_token_id, appointment_id

urlpatterns = [
    path('appt_token/', appointment_token),
    path('appt_token/<int:id>/', appointment_token_id),
    path('', appointment),
    path('<int:id>/', appointment_id)
]
