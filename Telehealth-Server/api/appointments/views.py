from django.http.response import JsonResponse
from rest_framework import status
from .models import AptToken, Appointment
from .serializers import AptTokenSerializer, AppointmentSerializer
from ..users.models import CustomUser, DoctorDetail
from ..views import check_authentication
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from ..users.serializers import UserSerializers


# Create your views here.
@csrf_exempt
def appointment_token(request):
    if request.method == 'POST':
        try:
            doctor_id = request.POST['doctor_id']
            symptoms = request.POST['symptoms']
            note = request.POST['note']
            slot = request.POST['slot']
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
            user = CustomUser.objects.get(pk=request.headers['Uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        # Doctor model validation.
        try:
            doctor_details = DoctorDetail.objects.get(pk=doctor_id)
            if not doctor_details.is_authorized:
                return JsonResponse({'ERR': 'Doctor is not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return JsonResponse({'ERR': 'Object not found.'}, status=404)
        # Date validation
        try:
            date_expected = datetime.strptime(r_date, '%d-%m-%Y').date()
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=400)

        # Create appointment token.
        try:
            apt_token = AptToken()
            if not note == '':
                apt_token.note = note
            apt_token.doctor_details = doctor_details
            apt_token.patient = user
            apt_token.slot = slot
            apt_token.symptoms = symptoms
            apt_token.date_expected = date_expected
            apt_token.save()
            return JsonResponse(AptTokenSerializer(apt_token).data)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

    if request.method == 'GET':
        # User authentication validation.
        try:
            res = check_authentication(request)
            if res.status_code != 200:
                return res
            else:
                del res
            user = CustomUser.objects.get(pk=request.headers['Uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        if user.is_doctor:
            try:
                doc_details = DoctorDetail.objects.get(doctor=user)
                apt_tokens = AptToken.objects.filter(doctor_details=doc_details, is_assigned=False)
                all_details = []
                for token in apt_tokens.values():
                    patient = CustomUser.objects.get(pk=token['patient_id'])
                    token['patient_name'] = patient.name
                    token['patient_age'] = int(date.today().year) - patient.birth_year
                    token['patient_gender'] = patient.gender
                    all_details.append(token)
                return JsonResponse(all_details, safe=False)
            except Exception as e:
                return JsonResponse({'ERR': str(e)}, status=500)
        else:
            try:
                apt_tokens = AptToken.objects.filter(patient=user)
                data = []
                for token in apt_tokens:
                    token_dict = dict(AptTokenSerializer(token).data)
                    token_dict['doctor'] = token.doctor_details.doctor.name
                    data.append(token_dict)
                return JsonResponse(data, safe=False)
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
            user = CustomUser.objects.get(pk=request.headers['Uid'])
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
            user = CustomUser.objects.get(pk=request.headers['Uid'])
            doc_details = DoctorDetail.objects.get(doctor=user)
            if not doc_details.is_authorized:
                return JsonResponse({'ERR': 'Unauthorized doctor.'}, status=401)
            if apt_token.doctor_details != doc_details:
                return JsonResponse({'ERR': 'Unauthorized access'}, status=401)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        # Parse datetime object
        try:
            date_time_obj = datetime.strptime(datetime_allocated, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=400)

        # Assign it
        try:
            appt = Appointment()
            appt.token = apt_token
            apt_token.is_assigned = True
            apt_token.save()
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
            user = CustomUser.objects.get(pk=request.headers['Uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        try:
            if user.is_doctor:
                doc_details = DoctorDetail.objects.get(doctor=user)
                if not doc_details.is_authorized:
                    return JsonResponse({'ERR': 'Unauthorized doctor.'}, status=401)
                doctor_appointments = Appointment.objects.filter(token__doctor_details=doc_details, is_treated=False)
                appointment_data = []
                for appt in doctor_appointments:
                    apptmt = dict(AppointmentSerializer(appt).data)
                    apptmt['patient_name'] = appt.token.patient.name
                    apptmt['patient_note'] = appt.token.note
                    apptmt['patient_age'] = int(date.today().year) - appt.token.patient.birth_year
                    apptmt['patient_symptoms'] = appt.token.symptoms
                    appointment_data.append(apptmt)
                return JsonResponse(appointment_data, safe=False)
            else:
                patient_appointments = Appointment.objects.filter(token__patient=user)
                res_data = []
                for patient_appt in patient_appointments:
                    patient_appt_dict = dict(AppointmentSerializer(patient_appt).data)
                    patient_appt_dict['doctor'] = patient_appt.token.doctor_details.doctor.name
                    patient_appt_dict['slot'] = patient_appt.token.slot
                    patient_appt_dict['symptoms'] = patient_appt.token.symptoms
                    patient_appt_dict['token_posted'] = patient_appt.token.time_posted
                    res_data.append(patient_appt_dict)
                return JsonResponse(res_data, safe=False)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)
    else:
        return JsonResponse({'ERR': 'Invalid request method.'}, status=405)


def appointment_id(request, id):
    if request.method == 'GET':
        # Validations
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        # Get required objects.
        try:
            user = CustomUser.objects.get(pk=request.headers['Uid'])
        except Exception as e:
            return JsonResponse({"ERR": str(e)}, status=500)

        try:
            appointment_obj = Appointment.objects.get(pk=id)
        except Exception as e:
            return JsonResponse({"ERR": str(e)}, status=404)

        # Authorization Validations:
        if user.is_doctor:
            if appointment_obj.token.doctor_details.doctor != user:
                return JsonResponse({"ERR": "Unauthorized access to this route."}, status=401)
        elif appointment_obj.token.patient != user:
            return JsonResponse({"ERR": "Unauthorized access to this route."}, status=401)

        # Return data to authorized users
        if user.is_doctor:
            patient = appointment_obj.token.patient
            apptmt = dict(AppointmentSerializer(appointment_obj).data)
            apptmt['patient_note'] = appointment_obj.token.note
            apptmt['patient_slot'] = appointment_obj.token.slot
            apptmt['patient_symptoms'] = appointment_obj.token.symptoms
            return JsonResponse(
                {'patient': UserSerializers(patient, context={'request': request}).data, 'appointment': apptmt})
        else:
            return JsonResponse(AppointmentSerializer(appointment_obj).data)


def get_four_days_arr():
    four_days_arr = []
    date_today = datetime.now()

    for i in range(1, 5):
        temp_date = date_today + timedelta(days=i)
        four_days_arr.append(temp_date)
    return four_days_arr


def get_available_slots(request, doc_id):
    if request.method == 'GET':
        try:
            DoctorDetail.objects.get(pk=doc_id)
        except Exception:
            return JsonResponse({"ERR": "Invalid Doctor id."})
        try:
            slots = ['Morning', 'Afternoon', 'Evening']
            availability = {}
            for day in get_four_days_arr():
                temp_avl_slots = []
                for slot in slots:
                    aptkn_day = AptToken.objects.filter(date_expected=day.date(), doctor_details__id=doc_id, slot=slot)
                    if len(aptkn_day) < 4:
                        temp_avl_slots.append(slot)
                        availability[day.strftime('%d-%m-%Y')] = temp_avl_slots
            return JsonResponse(availability, safe=False)
        except Exception as e:
            return JsonResponse({"ERR": str(e)})
    else:
        return JsonResponse({"ERR": "Invalid request method."}, status=403)
