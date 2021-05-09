from random import choice
import re
from datetime import datetime

from django.contrib.auth import get_user_model, login, logout
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from .models import CustomUser, DoctorDetail
from .serializers import UserSerializers, DoctorDetailSerializer
from ..views import check_authentication


# Create your views here.
def get_token(length: int = 10) -> str:
    return ''.join(choice(
        'asdfghjklzxcvbnmqwertyuiopASDFGHJKLZXCVBNMQWERTYUIOP132465987') for _ in range(length))


@csrf_exempt
def users(request) -> JsonResponse:
    if request.method == 'POST':
        try:
            name = request.POST['name']
            email = request.POST['email']
            phone = request.POST['phone']
            birth_year = request.POST['birth_year']
            gender = request.POST['gender']
            password = request.POST['password']
            is_doctor = request.POST['is_doctor']
            try:
                profile_photo = request.FILES['profile_photo']
            except Exception:
                profile_photo = None
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=400)

        # Validations
        if len(name.split(' ')) >= 4:
            return JsonResponse({'ERR': 'Name badly formated.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return JsonResponse({'ERR': 'Password should be greater than 6 chars.'}, status=status.HTTP_400_BAD_REQUEST)
        if re.match("//\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b/gi", email):
            return JsonResponse({"ERR": "Enter a valid email."}, status=status.HTTP_400_BAD_REQUEST)
        if len(phone) < 10 or len(phone) > 12:
            return JsonResponse({'ERR': 'Invalid phone number.'}, status=status.HTTP_400_BAD_REQUEST)
        if is_doctor == 'true':
            is_doctor = True
        else:
            is_doctor = False

        try:
            dob_object = datetime.strptime(birth_year, '%Y-%m-%d').year
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create User object
        try:
            new_user = CustomUser()
            new_user.is_doctor = is_doctor
            new_user.name = name
            new_user.birth_year = str(int(dob_object))
            new_user.gender = gender
            new_user.email = email
            new_user.phone = phone
            new_user.set_password(raw_password=password)
            new_user.auth_token = get_token()
            new_user.profile_photo = profile_photo
            new_user.save()
            login(request, user=new_user)
            user_serializer = UserSerializers(new_user, context={'request': request}, )
            return JsonResponse({'auth_token': new_user.auth_token, 'user': user_serializer.data},
                                status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'ERR': str(e)},
                                status=500)

    if request.method == 'GET':
        try:
            usrs = get_user_model()
            usrs = usrs.objects.filter(is_doctor=True).values()
        except Exception:
            return JsonResponse({'ERR': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        for i in usrs:
            i.pop('auth_token')
            i.pop("is_active")
            i.pop('is_staff')
            i.pop('is_superuser')
        return JsonResponse(list(usrs), safe=False)

    if request.method != 'GET' and request.method != 'POST':
        return JsonResponse({'ERR': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def users_id(request, id):
    if request.method == 'POST':
        try:
            email = request.POST['email']
        except Exception as e:
            email = None
        try:
            phone = request.POST['phone']
        except Exception:
            phone = None
        try:
            password = request.POST['password']
        except Exception:
            password = None
        try:
            profile_photo = request.FILES['profile_photo']
        except Exception:
            profile_photo = None

        # Validations

        # Authentication check
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        # Update usermod
        try:
            user = CustomUser.objects.get(pk=request.headers['Uid'])
            if email is not None:
                if user.email != email:
                    user.email = email
            if phone is not None:
                if user.phone != phone:
                    user.phone = phone
            if password == 'null':
                password = None
            if password is not None:
                user.set_password(raw_password=password)
            if profile_photo == 'null':
                user.profile_photo = None
            if profile_photo is not None:
                user.profile_photo = profile_photo
            user.save()
            return JsonResponse(UserSerializers(user, context={'request': request}).data)
        except Exception as e:
            print(e)
            return JsonResponse({'ERR': str(e)}, status=500)

    if request.method == 'GET':
        # Authentication check
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        try:
            user_model = get_user_model()
            user = user_model.objects.get(pk=id)
            if user.auth_token != request.headers['Authtoken']:
                return JsonResponse({'ERR': 'Action not allowed.'}, status=401)

            if user.is_doctor:
                try:
                    doctor_detls = DoctorDetail.objects.get(doctor=user)
                    return JsonResponse(
                        {'doctor_details': DoctorDetailSerializer(doctor_detls, context={'request': request}).data,
                         'user': UserSerializers(user, context={'request': request}).data})
                except Exception as e:
                    if str(e) == 'DoctorDetail matching query does not exist.':
                        return JsonResponse({'doctor_details': False, 'user': UserSerializers(user).data})
                    else:
                        return JsonResponse({'ERR': str(e)}, status=500)
            return JsonResponse(UserSerializers(user, context={'request': request}).data)
        except:
            return JsonResponse({'ERR': 'User not found.'}, status=404)

    if request.method == 'DELETE':
        # Authentication check
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        try:
            user_model = get_user_model()
            user = user_model.objects.get(pk=id)
            if user.auth_token != request.headers['Authtoken']:
                return JsonResponse({'ERR': 'Action not allowed.'}, status=401)
            user.delete()
            return JsonResponse({'INFO': f'Successfully deleted user with Uid : {id}'})
        except:
            return JsonResponse({'ERR': 'User not found.'}, status=404)

    if request.method != 'DELETE' and request.method != 'POST' and request.method != 'GET':
        return JsonResponse({'ERR': 'Invalid request.'}, status=400)


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            password = request.POST['password']
        except Exception as e:
            return JsonResponse({'ERR': "Parse Error on" + str(e)}, status=400)

        try:
            user = CustomUser.objects.get(email=email)
        except:
            return JsonResponse({'ERR': "Account with this email doesnot exsists."}, status=404)

        if user.check_password(password):
            token = get_token()
            user.auth_token = token
            user.save()
            if user.is_doctor:
                try:
                    doctor_detls = DoctorDetail.objects.get(doctor=user)
                    return JsonResponse(
                        {'doctor_details': DoctorDetailSerializer(doctor_detls, context={'request': request}).data,
                         'user': UserSerializers(user).data, 'auth_token': token})
                except Exception as e:
                    if str(e) == 'DoctorDetail matching query does not exist.':
                        return JsonResponse(
                            {'doctor_details': False, 'user': UserSerializers(user).data, 'auth_token': token})
                    else:
                        return JsonResponse({'ERR': str(e)}, status=500)
            login(request, user)
            return JsonResponse({'auth_token': token, 'user': UserSerializers(user).data})
        else:
            return JsonResponse({'ERR': 'Invalid auth credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return JsonResponse({'ERR': 'Invalid request'}, status=400)


@csrf_exempt
def signout(request, id):
    if request.method == 'GET':
        UserModel = CustomUser()
        try:
            user = UserModel.objects.get(pk=id)
            user.auth_token = "0"
            user.save()
            logout(request)
        except:
            return JsonResponse({'ERR': 'User not found'}, status=404)
        return JsonResponse({'INFO': 'Logged out successfully'})

    else:
        return JsonResponse({'ERR': 'Invalid request'}, status=400)


@csrf_exempt
def doctor_details(request):
    if request.method == 'POST':
        print(request.headers)
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        user = CustomUser.objects.get(pk=request.headers['Uid'])
        try:
            doctor = user
            specializations = request.POST['specializations']
            certificate = request.FILES['certificate']
            bio = request.POST['bio']
            open_time = request.POST['open_time']
            consultation_fee = request.POST['consultation_fee']
            city = request.POST['city']
        except Exception:
            return JsonResponse({'ERR': 'Parse error.'}, status=500)

        try:
            doctor_detail = DoctorDetail(doctor=doctor, specializations=specializations,
                                         certificate=certificate,
                                         bio=bio, open_time=open_time,
                                         consultation_fee=consultation_fee,
                                         city=city)
            doctor_detail.save()
            return JsonResponse(DoctorDetailSerializer(doctor_detail, context={'request': request}).data)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        try:
            doctors = DoctorDetail.objects.all()
            return JsonResponse(DoctorDetailSerializer(doctors, many=True).data, safe=False)
        except:
            return JsonResponse({'ERR': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'OPTIONS':
        print(request.headers)
        return JsonResponse({'ERR', "Invalid request method."}, status=403)


def check_auth(request):
    if request.method == 'GET':
        res = check_authentication(request)
        if res.status_code == 200:
            return JsonResponse({'Auth': True})
        else:
            return JsonResponse({'Auth': False})


@csrf_exempt
def doctor_details_id(request, d_id):
    if request.method == 'POST':
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        user = CustomUser.objects.get(pk=request.headers['Uid'])
        try:
            specializations = request.POST['specializations']
            bio = request.POST['bio']
            open_time = request.POST['open_time']
            consultation_fee = request.POST['consultation_fee']
            city = request.POST['city']
        except Exception:
            return JsonResponse({'ERR': 'Parse error.'}, status=500)

        try:
            doctor_detail = DoctorDetail.objects.get(pk=d_id)
            if doctor_detail.doctor != user:
                return JsonResponse({'ERR': "Detected Unauthorized Access."}, status=401)
            doctor_detail.specializations = specializations
            doctor_detail.bio = bio
            doctor_detail.open_time = open_time
            doctor_detail.consultation_fee = consultation_fee
            doctor_detail.city = city
            doctor_detail.save()
            return JsonResponse(DoctorDetailSerializer(doctor_detail, context={'request': request}).data)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def doctor_details_str(request, query):
    if request.method == 'GET':
        try:
            query_set = DoctorDetail.objects.filter(specializations__contains=query, is_authorized=True)
            res_data = []
            for query in query_set:
                doc_ser = dict(DoctorDetailSerializer(query, context={'request': request}).data)
                doc_ser['profile'] = dict(UserSerializers(query.doctor, context={'request': request}).data)
                res_data.append(doc_ser)
            return JsonResponse(res_data, safe=False)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=400)
    else:
        return JsonResponse({'ERR': "Invalid request method"}, status=401)
