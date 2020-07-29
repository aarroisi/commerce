from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def wlAmount(self):
        return len(self.wl_listings.filter(active="True"))

class Listing(models.Model):
    title = models.CharField(max_length=30)
    desc = models.TextField()
    starting_bid = models.PositiveIntegerField()
    image = models.CharField(max_length=1000, blank=True)
    category = models.CharField(max_length=30, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="all_listings")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    current_bid = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

class Watchlist(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wl_listings")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.creator.username} - {self.listing.title}"
    
class Bid(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    new_bid = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.creator.username} - {self.listing.title} - {self.new_bid}"