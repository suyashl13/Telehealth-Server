from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    name = models.CharField(max_length=38)
    email = models.EmailField(max_length=200, unique=True)
    phone = models.BigIntegerField(default=0, unique=True)
    gender = models.CharField(max_length=8, blank=True, default='')
    birth_year = models.IntegerField(blank=True, default=0)

    USERNAME_FIELD = 'email'
    is_doctor = models.BooleanField(default=False)
    auth_token = models.CharField(max_length=10)
    profile_photo = models.FileField(upload_to='profiles/', null=True, blank=True)
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'ID : {self.id} ' + f'({self.email})'


class DoctorDetail(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, unique=True)
    hospital_photos = models.ImageField(upload_to='profiles/')
    hospital_name = models.CharField(max_length=100)
    hospital_address = models.CharField(max_length=100, default='')
    specializations = models.CharField(max_length=150, default='')
    certificate = models.FileField(upload_to='certs/')
    bio = models.CharField(max_length=150)
    open_time = models.CharField(max_length=20)
    is_authorized = models.BooleanField(default=False)
    consultation_fee = models.IntegerField(default=0)

    def __str__(self):
        return self.doctor.name + ' - Hospital Details'
