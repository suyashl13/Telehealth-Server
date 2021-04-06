from django.contrib import admin
from .models import CustomUser, DoctorDetail

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(DoctorDetail)
