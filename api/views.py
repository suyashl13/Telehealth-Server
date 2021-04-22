from django.http.response import JsonResponse
from api.users.models import CustomUser, DoctorDetail


# Create your views here.
def home(request):
    return JsonResponse({'INFO': 'api home'})


def check_authentication(request: object, only_doctor: bool = False) -> JsonResponse:
    try:
        uid = request.headers['Uid']
        auth_token = request.headers['Authtoken']
    except Exception as e:
        return JsonResponse({'ERR': str(e)}, status=400)

    try:
        user = CustomUser.objects.get(pk=uid)
    except:
        return JsonResponse({'ERR': 'Invalid user id.'}, status=404)

    if only_doctor:
        try:
            doc_details = DoctorDetail.objects.get(doctor=user)
            if not doc_details.is_authorized:
                return JsonResponse({'ERR': 'Doctor is unauthorized'}, status=403)
            if not user.is_doctor:
                return JsonResponse({'ERR': 'Users not allowed'}, status=401)
        except Exception as e:
            return JsonResponse({'ERR': str(e)}, status=500)

    try:
        if user.auth_token != auth_token:
            return JsonResponse({'ERR': 'Invalid auth token'}, status=403)
        else:
            return JsonResponse({'INFO': 'user authenticated..'}, status=200)
    except:
        return JsonResponse({'ERR': 'Internal server error.'}, status=500)
