from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    login = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    job_title = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)