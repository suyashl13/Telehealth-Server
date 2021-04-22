from django.urls import path
from .views import users, users_id, signin, signout, doctor_details, check_auth, doctor_details_id

urlpatterns = [
    path('', users),
    path('<int:id>/', users_id),
    path('signin/', signin),
    path('signout/<int:id>/', signout),
    path('doctor_details/', doctor_details),
    path('check_auth/', check_auth),
    path('doctor_details/<int:d_id>/', doctor_details_id)
]
