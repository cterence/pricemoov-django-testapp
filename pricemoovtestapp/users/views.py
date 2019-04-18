from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from users.models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def user_create(request):
    if request.POST:
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users.views.user_list')
    else:
        form = UserForm()
    return render(request, 'user_create.html', {'form': form})


def user_update(request, id_user):
    user = get_object_or_404(User, id=id_user)
    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('users.views.user_list')
    return render(request, "user_create.html", {'form': form})


def user_delete(request, id_user):
    user = User.objects.get(id=id_user)
    user.delete()
    return redirect('users.views.user_list')
