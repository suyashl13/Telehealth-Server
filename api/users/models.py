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
    doc_choices = (
        ('FAMILY PHYSICIAN', 'FAMILY PHYSICIAN'),
        ('PODIATRIST', 'PODIATRIST'),
        ('SPORTS MEDICINE PHYSICIAN', 'SPORTS MEDICINE PHYSICIAN'),
        ('RADIOLOGIST', 'RADIOLOGIST'),
        ('PREVENTIVE MEDICINE PHYSICIAN', 'PREVENTIVE MEDICINE PHYSICIAN'),
        ('PHYSICAL MEDICINE AND REHABILITATION PHYSICIAN', 'PHYSICAL MEDICINE AND REHABILITATION PHYSICIAN'),
        ('DERMATOLOGIST', 'DERMATOLOGIST'),
        ('NUCLEAR MEDICINE PHYSICIAN', 'NUCLEAR MEDICINE PHYSICIAN'),
        ('OPHTHALMOLOGIST', 'OPHTHALMOLOGIST'),
        ('HOSPITALIST', 'HOSPITALIST'),
        ('ALLERGISTS AND IMMUNOLOGIST', 'ALLERGISTS AND IMMUNOLOGIST'),
        ('NEUROLOGIST', 'NEUROLOGIST'),
        ('PATHOLOGIST', 'PATHOLOGIST'),
        ('ANESTHESIOLOGIST', 'ANESTHESIOLOGIST'),
        ('SURGEON', 'SURGEON'),
        ('OBSTETRICIANS AND GYNECOLOGIST', 'OBSTETRICIANS AND GYNECOLOGIST'),
        ('PSYCHIATRIST', 'PSYCHIATRIST'),
        ('PEDIATRICIAN', 'PEDIATRICIAN'),
    )

    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, unique=True)
    specializations = models.CharField(max_length=150, default='', choices=doc_choices)
    certificate = models.FileField(upload_to='certs/')
    bio = models.CharField(max_length=150)
    open_time = models.CharField(max_length=20)
    is_authorized = models.BooleanField(default=False)
    consultation_fee = models.IntegerField(default=0)
    city = models.CharField(max_length=30, default='')

    def __str__(self):
        return self.doctor.name + f' ({self.id}) - Hospital Details'
