from django.contrib import admin

# Register your models here.
from .models import Treatment, Medicine

admin.site.register(Treatment)
admin.site.register(Medicine)