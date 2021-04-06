from django.urls import path
from .views import users, users_id, signin, signout

urlpatterns = [
    path('', users),
    path('<int:id>/', users_id),
    path('signin/', signin),
    path('signout/<int:id>/', signout),
]
