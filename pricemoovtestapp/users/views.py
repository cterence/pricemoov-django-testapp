from django.forms import ModelForm
from users.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
import base64, jwt, json, datetime
from rest_framework import views
from rest_framework.response import Response

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class Login(views.APIView): # Login class for JWT
    def post(self, request): # Post entrypoint
        if not request.data:
            return Response({'Error': "Please provide login/password"}, status="400")

        login = request.data['login']
        password = request.data['password']
        try:
            user = User.objects.get(login=login, password=password) # Try to get an user with provided credentials
        except User.DoesNotExist: # The user doesn't exist
            return Response({'Error': "Invalid login/password"}, status="400")
        if user:
            payload = { # Build the payload
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) # JWT expiration = 1 hour
            }
            jwt_token = {'token': jwt.encode(payload, "SECRET_KEY").decode("utf-8")}

            return HttpResponse( # Return the token if all everything is ok
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

def basic_or_jwt_auth_required(view): # Authentication decorator for both Basic and JWT
    def _decorator(request, *args, **kwargs):
        if ('HTTP_AUTHORIZATION') in request.META : # Find the HTTP_AUTHORIZATION header in the request
            try :
                auth_method, credentials = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            except ValueError :
                return HttpResponse({"Missing credentials"}, status="400")
            if auth_method.lower() == 'basic': # Basic method
                credentials = base64.b64decode(credentials.strip())
                login, password = credentials.decode().split(':', 1)
                try :
                    User.objects.get(login = login, password = password) # Try to match credentials with those stored in the database
                    return view(request, *args, **kwargs)
                except Exception:
                    return HttpResponseForbidden('Incorrect user credentials.')
            elif auth_method.lower() == 'bearer': # JWT method
                try:
                    payload = jwt.decode(credentials, "SECRET_KEY") # Decode the token and try to match the payload with the database
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

def get_current_user(request): # Get the current user using the credentials given in the request
    auth_method, credentials = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
    if auth_method.lower() == 'basic':  # Basic method
        credentials = base64.b64decode(credentials.strip())
        login, password = credentials.decode().split(':', 1)
        return User.objects.get(login = login, password = password)
    elif auth_method.lower() == 'bearer':  # JWT method
        payload = jwt.decode(credentials, "SECRET_KEY")
        id = payload['id']
        first_name = payload['first_name']
        last_name = payload['last_name']
        return User.objects.get(
            id=id,
            first_name=first_name,
            last_name=last_name
        )

@basic_or_jwt_auth_required
def user_list(request, template_name='users/user_list.html'): # User list viex
    current_user = get_current_user(request)
    if (current_user.is_admin) : # If admin, list every user
        user = User.objects.all()
        data = {}
        data['object_list'] = user
        return render(request, template_name, data)
    else :
        user = User.objects.filter(id = current_user.id) # If not admin, list only the current user
        data = {}
        data['object_list'] = user
        return render(request, template_name, data)

@basic_or_jwt_auth_required
def user_create(request, template_name='users/user_form.html'):
    current_user = get_current_user(request)
    if (current_user.is_admin): # Only allow creation when admin
        form = UserForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('user_list')
        return render(request, template_name, {'form':form})
    else :
        return HttpResponseForbidden('You don\'t have the privileges to create a new user.')

@basic_or_jwt_auth_required
def user_update(request, pk, template_name='users/user_form.html'): # User update route
    current_user = get_current_user(request)
    if (current_user.is_admin): # If admin, allowed to update any user
        user= get_object_or_404(User, pk=pk)
        form = UserForm(request.POST or None, instance=user)
        if (current_user.id == pk): # Prevent an admin to remove his privileges
            form.fields.pop('is_admin')
        if form.is_valid():
            form.save()
            return redirect('user_list')
        return render(request, template_name, {'form':form})
    else :
        if (pk != current_user.id): # Check if the current user is the user that he wants to edit
            return HttpResponseForbidden('You don\'t have the privileges to edit an user.')
        else :
            user = get_object_or_404(User, pk=pk)
            form = UserForm(request.POST or None, instance=user)
            form.fields.pop('is_admin') # Prevent the possibility of a non admin user to update his admin field
            if form.is_valid():
                form.save()
                return redirect('user_list')
            return render(request, template_name, {'form': form})

@basic_or_jwt_auth_required
def user_delete(request, pk, template_name='users/user_confirm_delete.html'): # User delete route
    current_user = get_current_user(request)
    if (current_user.is_admin):
        if (pk == current_user.id): # Disallow admin to delete its profile
            return HttpResponseForbidden('You can\'t delete your own profile.')
        else :
            user= get_object_or_404(User, pk=pk)
            if request.method=='POST':
                user.delete()
                return redirect('user_list')
            return render(request, template_name, {'object':user})

    else : # Disallow any non admin to delete anything
        return HttpResponseForbidden('You don\'t have the privileges to delete an user. ')

def first_user(request, template_name='users/user_form.html'): # First user view
    user = User.objects.all() # Check if there is any entry in the db
    if (user) : # Disallow the use of the route if there is an entry
        return HttpResponseForbidden('You can\'t create a first user when there is already an user in the database.')
    else : # Allow the use if the db is empty
        form = UserForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False) # Force the first user to be an admin
            instance.is_admin = True
            instance.save()
            return redirect('user_list')
        form.fields.pop('is_admin')
        return render(request, template_name, {'form': form})