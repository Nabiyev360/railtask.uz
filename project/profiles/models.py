from django.contrib.auth.models import User
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Profile(models.Model):
    ROLE_CHOICES = (
        ('assigner', 'Buyuruvchi'),
        ('performer', 'Ijrochi'),
        ('dual', 'Buyuruvchi hamda ijrochi'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='profiles')
    position = models.CharField(max_length=150)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    tg_id = models.IntegerField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.full_name

