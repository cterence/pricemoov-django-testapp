from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from users.models import User
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy



class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class UserList(ListView):
    model = User

class UserView(DetailView):
    model = User

class UserCreate(CreateView):
    model = User
    fields = ['first_name', 'last_name', 'login', 'email', 'job_title']
    success_url = reverse_lazy('user_list')

class UserUpdate(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'login', 'email', 'job_title']
    success_url = reverse_lazy('user_list')

class UserDelete(DeleteView):
    model = User
    success_url = reverse_lazy('user_list')


