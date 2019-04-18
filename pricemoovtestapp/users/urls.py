from django.urls import path

from . import views

urlpatterns = [
    path('user_list', views.user_list, name='user_list'),
    path('user_create', views.user_create, name='user_create')
]
