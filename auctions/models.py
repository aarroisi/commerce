from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=30)
    desc = models.TextField()
    bid = models.PositiveIntegerField()
    image = models.CharField(max_length=1000, blank=True)
    category = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.title