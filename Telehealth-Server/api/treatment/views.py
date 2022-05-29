from datetime import datetime

from django.http.response import JsonResponse
from ..views import check_authentication
from ..appointments.models import Appointment
from ..users.models import CustomUser, DoctorDetail
from .models import Treatment, Medicine
from .serilizers import TreatmentSerializer, MedicineSerializer
from django.views.decorators.csrf import csrf_exempt
from ..users.serializers import UserSerializers


# Create your views here.
@csrf_exempt
def treatment(request):
    if request.method == 'POST':
        res = check_authentication(request, only_doctor=True)
        if res.status_code != 200:
            return res
        else:
            del res
        try:
            try:
                appointment = request.POST['appointment']
            except Exception as e:
                return JsonResponse({'ERR': str(e)}, 400)
            precautions = request.POST['precautions']
        except Exception:
            precautions = None

        try:
            doc_user = CustomUser.objects.get(id=request.headers['Uid'])
            doc_details = DoctorDetail.objects.get(doctor=doc_user)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        try:
            appt = Appointment.objects.get(id=appointment)
            appt.is_treated = True
            appt.save()
            if appt.token.doctor_details != doc_details:
                return JsonResponse({'ERR': 'Unauthorized Access to route.'}, status=401)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        try:
            trtmt = Treatment()
            trtmt.appointment = appt
            trtmt.doctor = appt.token.doctor_details
            trtmt.patient = appt.token.patient
            trtmt.precautions = precautions
            if len(Treatment.objects.filter(appointment=appt)) != 0:
                return JsonResponse({'ERR': 'Already treated.'}, status=401)
            trtmt.save()
            return JsonResponse(TreatmentSerializer(trtmt).data)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

    elif request.method == 'GET':
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        try:
            user = CustomUser.objects.get(id=request.headers['Uid'])
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

        try:
            if user.is_doctor:
                doc_details = DoctorDetail.objects.get(doctor=user)
                treatments = Treatment.objects.filter(doctor=doc_details)
                all_treatments = []
                for trtmt in treatments:
                    tmt = dict(TreatmentSerializer(trtmt).data)
                    tmt['symptoms'] = trtmt.appointment.token.symptoms
                    tmt['patient'] = dict(UserSerializers(trtmt.patient, context={'request': request}).data)
                    tmt['medecines'] = get_meds_by_treatment_id(tmt['id'])
                    all_treatments.append(tmt)
                return JsonResponse(all_treatments, safe=False)
            else:
                treatments = Treatment.objects.filter(patient=user)
                all_treatments = []
                for trtmt in treatments:
                    tmt = dict(TreatmentSerializer(trtmt).data)
                    tmt['symptoms'] = trtmt.appointment.token.symptoms
                    tmt['doctor'] = trtmt.appointment.token.doctor_details.doctor.name
                    tmt['doctor_phone'] = trtmt.appointment.token.doctor_details.doctor.phone
                    tmt['doctor_specialization'] = trtmt.appointment.token.doctor_details.specializations
                    tmt['patient'] = dict(UserSerializers(trtmt.patient).data)
                    tmt['medecines'] = get_meds_by_treatment_id(tmt['id'])
                    all_treatments.append(tmt)
                return JsonResponse(all_treatments, safe=False)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)
    else:
        return JsonResponse({'ERR': 'Invalid request method'}, status=403)


@csrf_exempt
def medicine_id(request, id):
    if request.method == 'POST':
        res = check_authentication(request, only_doctor=True)
        if res.status_code != 200:
            return res
        else:
            del res

        try:
            try:
                medicine = request.POST['medicine_name']
                intake_quantity = request.POST['intake_quantity']
                duration = request.POST['duration']
                note = request.POST['note']
                intake_time_1 = request.POST['intake_time_1']
                intake_time_2 = request.POST['intake_time_2']
                intake_time_3 = request.POST['intake_time_3']
            except Exception as e:
                return JsonResponse({'ERR': "Invalid " + str(e)}, status=400)
            intake_time_4 = request.POST['intake_time_4']
        except Exception:
            intake_time_4 = None

        try:
            intake_time_1_obj = datetime.strptime(intake_time_1, '%H:%M').time()
            intake_time_2_obj = datetime.strptime(intake_time_2, '%H:%M').time()
            intake_time_3_obj = datetime.strptime(intake_time_3, '%H:%M').time()
            try:
                if intake_time_4 is not None:
                    intake_time_4_obj = datetime.strptime(intake_time_4, '%H:%M').time()
            except Exception:
                pass
        except Exception as e:
            return JsonResponse({'ERR1': str(e)})

        try:
            treatment = Treatment.objects.get(pk=id)
            doc_det = DoctorDetail.objects.get(doctor__id=request.headers['Uid'])
            if treatment.doctor != doc_det:
                return JsonResponse({'ERR': 'Unauthorized access to this route'}, status=401)
            med = Medicine()
            med.treatment = treatment
            med.medicine = medicine
            med.intake_quantity = intake_quantity
            med.duration = duration
            med.note = note
            med.intake_time_1 = intake_time_1_obj
            med.intake_time_2 = intake_time_2_obj
            med.intake_time_3 = intake_time_3_obj
            try:
                if intake_time_4 is not None:
                    med.intake_time_4 = intake_time_4_obj
            except Exception:
                pass
            med.save()
            return JsonResponse({'INFO': 'Successfully added med.', 'med': MedicineSerializer(med).data}, status=200)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

    if request.method == 'GET':
        res = check_authentication(request, only_doctor=False)
        if res.status_code != 200:
            return res
        else:
            del res

        try:
            user = CustomUser.objects.get(id=request.headers['Uid'])
            if user.is_doctor:
                doc_details = DoctorDetail.objects.get(doctor=request.headers['Uid'])
            try:
                treatment = Treatment.objects.get(id=id)
                if treatment.doctor == doc_details or treatment.patient == user:
                    meds = Medicine.objects.filter(treatment=treatment)
                    return JsonResponse(MedicineSerializer(meds, many=True).data, safe=False)
            except Exception as e:
                return JsonResponse({'ERR': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=400)
    else:
        return JsonResponse({'ERR': 'Bad request method'}, status=401)


@csrf_exempt
def treatment_id(request, id):
    if request.method == 'POST':
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res
        try:
            is_completed = request.POST['is_completed']
            if is_completed == 'true':
                is_completed = True
            else:
                is_completed = False
        except Exception:
            pass

        try:
            user = CustomUser.objects.get(id=request.headers['Uid'])
            if user.is_doctor:
                doc_user = CustomUser.objects.get(id=request.headers['Uid'])
                doc_details = DoctorDetail.objects.get(doctor=doc_user)
                treatment = Treatment.objects.get(id=id)
                treatment.is_treated = is_completed
                treatment.save()
            treatment = Treatment.objects.get(id=id)
            if treatment.patient == user:
                treatment.is_treated = is_completed
                treatment.save()
                return JsonResponse(TreatmentSerializer(treatment).data)
            else:
                return JsonResponse({'ERR': 'Unauthorized'}, status=401)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)
    elif request.method == 'GET':
        res = check_authentication(request, only_doctor=True)
        if res.status_code != 200:
            return res
        else:
            del res

        try:
            user = CustomUser.objects.get(id=request.headers['Uid'])
            doc_user = CustomUser.objects.get(id=request.headers['Uid'])
            doc_details = DoctorDetail.objects.get(doctor=doc_user)
            treatment = Treatment.objects.get(id=id)
            if treatment.patient != user or treatment.doctor != doc_details:
                return JsonResponse(TreatmentSerializer(treatment).data)
            else:
                return JsonResponse({'ERR': 'Unauthorized'}, status=401)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)
    else:
        return JsonResponse({'ERR': 'Invalid request method.'}, status=400)


# Dependent Methods.
def get_meds_by_treatment_id(treatment_id: int):
    meds = Medicine.objects.filter(treatment=Treatment.objects.get(pk=treatment_id))
    all_meds = []
    for med in meds:
        d_med = dict(MedicineSerializer(med).data)
        all_meds.append(d_med)
    del meds
    return all_meds
