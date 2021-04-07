from .models import CustomUser, DoctorDetail
from rest_framework.serializers import HyperlinkedModelSerializer, ImageField


class UserSerializers(HyperlinkedModelSerializer):
    profile_photo = ImageField(max_length=None, allow_empty_file=True, required=False)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(raw_password=password)
        instance.save()

        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(raw_password=value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = CustomUser
        extra_kwargs = {'password': {'write_only': True}}
        fields = (
            'id', 'name', 'email', 'password', 'phone', 'auth_token', 'is_doctor', 'profile_photo', 'gender',
            'birth_year')


class DoctorDetailSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = DoctorDetail
        fields = ['hospital_photos',
                  'hospital_name',
                  'hospital_address',
                  'specializations',
                  'certificate',
                  'bio',
                  'open_time', 'consultation_fee', 'city']
