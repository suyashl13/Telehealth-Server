from django.db import models
from ..users.models import CustomUser, DoctorDetail
from ..appointments.models import Appointment


# Create your models here.
class Treatment(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorDetail, on_delete=models.CASCADE)

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, unique=True)
    precautions = models.CharField(max_length=100)

    date_created = models.DateField(auto_now=True)
    is_treated = models.BooleanField(default=False)


class Medicine(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    medicine = models.CharField(max_length=80)
    intake_quantity = models.CharField(max_length=10)
    total_quantity = models.CharField(max_length=10,default='')

    intake_time_1 = models.TimeField()
    intake_time_2 = models.TimeField()
    intake_time_3 = models.TimeField()
    intake_time_4 = models.TimeField(null=True, blank=True)

    datetime_created = models.DateTimeField(auto_now=True)
