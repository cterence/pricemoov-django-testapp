from django.forms import ModelForm
from users.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
import base64, jwt, json, datetime
from rest_framework import status, exceptions, views
from rest_framework.response import Response

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class Login(views.APIView):
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({'Error': "Please provide login/password"}, status="400")

        login = request.data['login']
        password = request.data['password']
        try:
            user = User.objects.get(login=login, password=password)
        except User.DoesNotExist:
            return Response({'Error': "Invalid login/password"}, status="400")
        if user:
            payload = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            jwt_token = {'token': jwt.encode(payload, "SECRET_KEY").decode("utf-8")}

            return HttpResponse(
                json.dumps(jwt_token),
                status=200,
                content_type="application/json"
        )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )

def basic_or_jwt_auth_required(view):
    def _decorator(request, *args, **kwargs):
        if ('HTTP_AUTHORIZATION') in request.META :
            try :
                auth_method, credentials = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            except ValueError :
                return HttpResponse({"Missing credentials"}, status="400")
            if auth_method.lower() == 'basic': # Basic method
                credentials = base64.b64decode(credentials.strip())
                login, password = credentials.decode().split(':', 1)
                try :
                    User.objects.get(login = login, password = password)
                    return view(request, *args, **kwargs)
                except Exception:
                    return HttpResponseForbidden('Incorrect user credentials.')
            elif auth_method.lower() == 'bearer': # JWT method
                try:
                    payload = jwt.decode(credentials, "SECRET_KEY")
                    id = payload['id']
                    first_name = payload['first_name']
                    last_name = payload['last_name']
                    User.objects.get(
                        id=id,
                        first_name=first_name,
                        last_name=last_name
                    )
                    return view(request, *args, **kwargs)

                except jwt.DecodeError or jwt.InvalidTokenError or jwt.InvalidSignatureError:
                    return HttpResponse({"Token is invalid"}, status="403")
                except jwt.ExpiredSignatureError:
                    return HttpResponse({"Token has expired"}, status="403")
                except User.DoesNotExist:
                    return HttpResponse({"The user does not exist"}, status="404")

            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic or JWT'
            return response
        else:
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic or JWT'
            return response
    return _decorator

@basic_or_jwt_auth_required
def user_list(request, template_name='users/user_list.html'):
    user = User.objects.all()
    data = {}
    data['object_list'] = user
    return render(request, template_name, data)

@basic_or_jwt_auth_required
def user_create(request, template_name='users/user_form.html'):
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, template_name, {'form':form})

@basic_or_jwt_auth_required
def user_update(request, pk, template_name='users/user_form.html'):
    user= get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, template_name, {'form':form})

@basic_or_jwt_auth_required
def user_delete(request, pk, template_name='users/user_confirm_delete.html'):
    user= get_object_or_404(User, pk=pk)
    if request.method=='POST':
        user.delete()
        return redirect('user_list')
    return render(request, template_name, {'object':user})