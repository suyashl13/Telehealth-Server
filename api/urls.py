from django.urls import path, include
from .views import home

urlpatterns = [
    path('', home),
    path('users/', include('api.users.urls'))
]