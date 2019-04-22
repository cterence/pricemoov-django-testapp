from django.urls import include, path
from users.views import Login

urlpatterns = [
    path('users/', include('users.urls')),
    path('login/', Login.as_view(), name='login')
]
