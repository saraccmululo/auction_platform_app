from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watched_by")

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

class Listing(models.Model):
    title= models.CharField(max_length=30)
    description=models.TextField()
    image_url=models.URLField(blank=True, null=True)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    start_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_listing")
    created_at = models.DateTimeField(default=timezone.now)
    winner=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_listing")

    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"${self.amount} by {self.user.username} on {self.listing.title}"

class Comment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text= models.TextField(default="")
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}: {self.text[:20]}"

