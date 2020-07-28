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
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="all_listings")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title