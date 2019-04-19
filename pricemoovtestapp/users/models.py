from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    login = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=200, unique=True)
    job_title = models.CharField(max_length=200)

    def __str__(self):
        return self.login

    def get_absolute_url(self):
        return reverse('user_edit', kwargs={'login': self.login})