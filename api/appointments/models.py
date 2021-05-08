from django.db import models
from ..users.models import DoctorDetail, CustomUser


# Create your models here.
class AptToken(models.Model):
    slots = (('Morning', 'Morning'),
             ('Afternoon', 'Afternoon'),
             ('Evening', 'Evening'),)

    doctor_details = models.ForeignKey(DoctorDetail, on_delete=models.CASCADE)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    symptoms = models.CharField(max_length=200)
    note = models.CharField(max_length=50, blank=True, null=True)
    date_expected = models.DateField()
    slot = models.CharField(max_length=10, default='', blank=False, choices=slots)
    is_assigned = models.BooleanField(default=False)
    time_posted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id} -> {self.patient.name} ({self.time_posted})'


class Appointment(models.Model):
    token = models.ForeignKey(AptToken, on_delete=models.CASCADE, unique=True)
    note = models.CharField(max_length=52, blank=True, null=True)
    datetime_allocated = models.DateTimeField()
    time_posted = models.DateTimeField(auto_now=True)
    is_treated = models.BooleanField(default=False)
