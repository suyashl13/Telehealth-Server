from django.urls import path
from .views import appointment_token, appointment, appointment_token_id, appointment_id, get_available_slots

urlpatterns = [
    path('appt_token/', appointment_token),
    path('appt_token/<int:id>/', appointment_token_id),
    path('', appointment),
    path('available_slots/<int:doc_id>/', get_available_slots),
    path('<int:id>/', appointment_id)
]
