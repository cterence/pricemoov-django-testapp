from django.urls import path

from . import views


urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('new', views.user_create, name='user_new'),
    path('first', views.first_user, name='first_user'),
    path('edit/<int:pk>', views.user_update, name='user_edit'),
    path('delete/<int:pk>', views.user_delete, name='user_delete'),
]
