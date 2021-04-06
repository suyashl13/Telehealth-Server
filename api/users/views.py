from random import choice
import re
import sys

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
            profile_photo = request.FILES['profile_photo']
        except:
            return JsonResponse({'ERR': 'Parse Error on received request.'})

        # Validations
        if len(name.split(' ')) >= 3:
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

        # Create User object
        try:
            new_user = CustomUser()
            new_user.is_doctor = is_doctor
            new_user.name = name
            new_user.birth_year = str(int(birth_year))
            new_user.gender = gender
            new_user.email = email
            new_user.phone = phone
            new_user.set_password(raw_password=password)
            new_user.auth_token = get_token()
            new_user.profile_photo = profile_photo
            new_user.save()
            login(request, user=new_user)
        except:
            return JsonResponse({'ERR': "Unexpected error:" + str(sys.exc_info()[0])},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_serializer = UserSerializers(new_user)
        return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)

    if request.method == 'GET':
        try:
            usrs = get_user_model()
            usrs = usrs.objects.filter(is_doctor=True).values()
        except:
            return JsonResponse({'ERR': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        for i in usrs:
            i.pop('auth_token')
            i.pop("is_active")
            i.pop('is_staff')
            i.pop('is_superuser')
        return JsonResponse(list(usrs), safe=False)

    if request.method != 'GET' and request.method != 'POST':
        return JsonResponse({'ERR': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


def users_id(request, id):
    if request.method == 'PUT':
        try:
            name = request.PUT['name']
            email = request.PUT['email']
            phone = request.PUT['phone']
            birth_year = request.PUT['age']
            gender = request.PUT['gender']
            password = request.PUT['password']
            profile_photo = request.FILES['profile_photo']
        except:
            return JsonResponse({'ERR': 'Parse Error on received request.'})

        # Validations
        if len(name.split(' ')) >= 3:
            return JsonResponse({'ERR': 'Name badly formated.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return JsonResponse({'ERR': 'Password should be greater than 6 chars.'}, status=status.HTTP_400_BAD_REQUEST)
        if re.match("//\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b/gi", email):
            return JsonResponse({"ERR": "Enter a valid email."}, status=status.HTTP_400_BAD_REQUEST)
        if len(phone) < 10 or len(phone) > 12:
            return JsonResponse({'ERR': 'Invalid phone number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Authentication check
        res = check_authentication(request)
        if res.status_code != 200:
            return res
        else:
            del res

        # Update usermodel
        try:
            user_model = get_user_model()
            user = user_model.objects.get(pk=id)
            if user.auth_token != request.headers['authtoken']:
                return JsonResponse({'ERR': 'Action not allowed.'}, status=401)
        except:
            return JsonResponse({'ERR': 'User not found.'}, status=404)

        try:
            user.name = name
            user.birth_year = int(birth_year)
            user.gender = gender
            user.email = email
            user.phone = phone
            user.set_password(raw_password=password)
            user.profile_photo = profile_photo
            user.save()
        except:
            return JsonResponse({'ERR': 'Unable to update user details'}, status=400)

        return JsonResponse(UserSerializers(user).data)

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
            if user.auth_token != request.headers['authtoken']:
                return JsonResponse({'ERR': 'Action not allowed.'}, status=401)
            return JsonResponse(UserSerializers(user).data)
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
            if user.auth_token != request.headers['authtoken']:
                return JsonResponse({'ERR': 'Action not allowed.'}, status=401)
            user.delete()
            return JsonResponse({'INFO': f'Successfully deleted user with uid : {id}'})
        except:
            return JsonResponse({'ERR': 'User not found.'}, status=404)

    if request.method != 'DELETE' and request.method != 'PUT' and request.method != 'GET':
        return JsonResponse({'ERR': 'Invalid request.'}, status=400)


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            password = request.POST['password']
        except:
            return JsonResponse({'ERR': "Unable to parse request."})

        try:
            user = CustomUser.objects.get(email=email)
        except:
            return JsonResponse({'ERR': "Account with this email doesnot exsists."}, status=404)
        try:
            if user.check_password(password):
                token = get_token()
                user.auth_token = token
                if user.is_doctor:
                    try:
                        doc_details = DoctorDetail.objects.get(doctor=user)
                    except:
                        return JsonResponse({'auth_token': token,
                                             'ERR': 'Looks like you have`nt provided hospital details. Please provide details at '
                                                    + str(request.META['SERVER_PROTOCOL']).lower().split('/')[0]+'://'+str(request.META['REMOTE_ADDR'])+':'+request.META['SERVER_PORT']+'/doctor_details/uid/token/',
                                             'user': UserSerializers(user).data}, status=401)
                    return JsonResponse({'auth_token': token, doc_details: DoctorDetailSerializer(doc_details).data,
                                         user: UserSerializers(user).data})
                user.save()
                login(request, user)
                return JsonResponse(UserSerializers(user).data)
            else:
                return JsonResponse({'ERR': 'Invalid auth credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return JsonResponse({'ERR': 'Unable to login due to server error.'}, status=500)
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
