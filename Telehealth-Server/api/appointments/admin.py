from django.contrib import admin
from .models import AptToken, Appointment

# Register your models here.
admin.site.register(Appointment)
admin.site.register(AptToken)
