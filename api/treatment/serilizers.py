from rest_framework.serializers import ModelSerializer
from .models import Treatment, Medicine


class TreatmentSerializer(ModelSerializer):
    class Meta:
        model = Treatment
        fields = '__all__'


class MedicineSerializer(ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
