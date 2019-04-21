from django.forms import ModelForm
from users.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
import base64

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'

# The basic auth decorator
def login_or_basic_auth_required(view):
    def _decorator(request, *args, **kwargs):
        if ('HTTP_AUTHORIZATION') in request.META :
            auth_method, credentials = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if auth_method.lower() == 'basic':
                credentials = base64.b64decode(credentials.strip())
                username, password = credentials.decode().split(':', 1)
                try :
                    User.objects.get(login = username, password = password)
                    return view(request, *args, **kwargs)
                except Exception:
                    return HttpResponseForbidden('Incorrect user credentials.')
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic'
            return response
        else:
            if request.user.is_authenticated:
                return view(request, *args, **kwargs)
            else:
                response = HttpResponse()
                response.status_code = 401
                response['WWW-Authenticate'] = 'Basic'
                return response
    return _decorator

@login_or_basic_auth_required
def user_list(request, template_name='users/user_list.html'):
    user = User.objects.all()
    data = {}
    data['object_list'] = user
    return render(request, template_name, data)

@login_or_basic_auth_required
def user_create(request, template_name='users/user_form.html'):
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, template_name, {'form':form})

@login_or_basic_auth_required
def user_update(request, pk, template_name='users/user_form.html'):
    user= get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, template_name, {'form':form})

@login_or_basic_auth_required
def user_delete(request, pk, template_name='users/user_confirm_delete.html'):
    user= get_object_or_404(User, pk=pk)
    if request.method=='POST':
        user.delete()
        return redirect('user_list')
    return render(request, template_name, {'object':user})