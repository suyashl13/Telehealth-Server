from django.http.response import JsonResponse
from rest_framework import status
from .models import AptToken, Appointment
from .serializers import AptTokenSerializer, AppointmentSerializer
from ..users.models import CustomUser, DoctorDetail
from ..views import check_authentication
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def appointment_token(request):
    if request.method == 'POST':
        try:
            doctor_id = request.POST['doctor_id']
            symptoms = request.POST['symptoms']
            note = request.POST['note']
            r_date = request.POST['date_expected']
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Validations
        # User authentication validation.
        try:
            res = check_authentication(request)
            if res.status_code != 200:
                return res
            else:
                del res
            user = CustomUser.objects.get(pk=request.headers['uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        # Doctor model validation.
        try:
            doctor_details = DoctorDetail.objects.get(pk=doctor_id)
            if not doctor_details.is_authorized:
                return JsonResponse({'ERR': 'Doctor is not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return JsonResponse({'ERR': 'Object not found.'}, status=404)
        # Date validation
        try:
            date_expected = datetime.strptime(r_date, '%d/%m/%Y').date()
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=400)

        # Create appointment token.
        try:
            apt_token = AptToken()
            if not note == '':
                apt_token.note = note
            apt_token.doctor_details = doctor_details
            apt_token.patient = user
            apt_token.symptoms = symptoms
            apt_token.date_expected = date_expected
            apt_token.save()
            return JsonResponse(AptTokenSerializer(apt_token).data)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

    if request.method == 'GET':
        # Validations
        # User authentication validation.
        try:
            res = check_authentication(request)
            if res.status_code != 200:
                return res
            else:
                del res
            user = CustomUser.objects.get(pk=request.headers['uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        if user.is_doctor:
            try:
                doc_details = DoctorDetail.objects.get(doctor=user)
                apt_tokens = AptToken.objects.filter(doctor_details=doc_details)
                return JsonResponse(AptTokenSerializer(apt_tokens, many=True).data, safe=False)
            except Exception as e:
                return JsonResponse({'ERR': str(e)}, status=500)
        else:
            try:
                apt_tokens = AptToken.objects.filter(patient=user)
                return JsonResponse(AptTokenSerializer(apt_tokens, many=True).data, safe=False)
            except Exception as e:
                return JsonResponse({'ERR': str(e)}, status=500)
    else:
        return JsonResponse({'ERR': 'Invalid request method.'}, status=400)


@csrf_exempt
def appointment_token_id(request, id):
    if request.method == 'GET':
        # Validations
        # User authentication validation.
        try:
            res = check_authentication(request)
            if res.status_code != 200:
                return res
            else:
                del res
            user = CustomUser.objects.get(pk=request.headers['uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        if user.is_doctor:
            try:
                doc_details = DoctorDetail.objects.get(doctor=user)
                apt_tokens = AptToken.objects.get(doctor_details=doc_details, id=id)
                return JsonResponse(AptTokenSerializer(apt_tokens, many=True).data, safe=False)
            except Exception as e:
                return JsonResponse({'ERR': str(e)}, status=500)
        else:
            try:
                apt_tokens = AptToken.objects.get(patient=user, id=id)
                return JsonResponse(AptTokenSerializer(apt_tokens).data)
            except Exception as e:
                return JsonResponse({'ERR': str(e)}, status=500)
    else:
        return JsonResponse({'ERR': 'Invalid request method.'}, status=405)


@csrf_exempt
def appointment(request):
    if request.method == 'POST':
        # Parameters
        try:
            token_id = request.POST['token']
            datetime_allocated = request.POST['datetime']
            note = request.POST['note']
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        # Validations
        res = check_authentication(request, only_doctor=True)
        if res.status_code != 200:
            return res
        else:
            del res
        try:
            apt_token = AptToken.objects.get(pk=token_id)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=404)

        # Get DoctorDetails and validate:
        try:
            user = CustomUser.objects.get(pk=request.headers['uid'])
            doc_details = DoctorDetail.objects.get(doctor=user)
            if not doc_details.is_authorized:
                return JsonResponse({'ERR': 'Unauthorized doctor.'}, status=401)
            if apt_token.doctor_details != doc_details:
                return JsonResponse({'ERR': 'Unauthorized access'}, status=401)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        # Parse datetime object
        try:
            date_time_obj = datetime.strptime(datetime_allocated, '%d/%m/%Y %H:%M:%S')
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=400)

        # Assign it
        try:
            appt = Appointment()
            appt.token = apt_token
            if note != '':
                appt.note = note
            appt.datetime_allocated = date_time_obj
            appt.save()
            return JsonResponse(AppointmentSerializer(appt).data)
        except Exception as e:
            if str(e).split(':')[0] == 'UNIQUE constraint failed':
                return JsonResponse({'ERR': 'Duplicate appointment detected.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            return JsonResponse({'ERR': str(e)}, status=500)

    elif request.method == 'GET':
        # Validations
        res = check_authentication(request, only_doctor=False)
        if res.status_code != 200:
            return res
        else:
            del res

        # Get DoctorDetails and validate:
        try:
            user = CustomUser.objects.get(pk=request.headers['uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        try:
            if user.is_doctor:
                doc_details = DoctorDetail.objects.get(doctor=user)
                if not doc_details.is_authorized:
                    return JsonResponse({'ERR': 'Unauthorized doctor.'}, status=401)
                doctor_appointments = Appointment.objects.filter(token__doctor_details=doc_details)
                return JsonResponse(AppointmentSerializer(doctor_appointments, many=True).data, safe=False)
            else:
                patient_appointments = Appointment.objects.filter(token__patient=user)
                return JsonResponse(AppointmentSerializer(patient_appointments, many=True).data, safe=False)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)
    else:
        return JsonResponse({'ERR': 'Invalid request method.'}, status=405)

