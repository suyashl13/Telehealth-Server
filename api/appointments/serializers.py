from rest_framework.serializers import ModelSerializer
from .models import AptToken, Appointment


class AptTokenSerializer(ModelSerializer):
    class Meta:
        model = AptToken
        fields = (
            'doctor_details',
            'patient',
            'symptoms',
            'note',
            'date_expected',
            'slot',
            'is_assigned',
            'time_posted',
        )


class AppointmentSerializer(ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'id', 'token',
            'note', 'is_treated',
            'datetime_allocated', 'time_posted',
        )
