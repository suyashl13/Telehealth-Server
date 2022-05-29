from django.urls import path
from .views import treatment, medicine_id, treatment_id

urlpatterns = [
    path('', treatment),
    path('<int:id>/', treatment_id),
    path('medicine/<int:id>/', medicine_id),
]
