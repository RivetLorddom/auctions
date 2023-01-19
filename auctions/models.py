from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", related_name="watched_by", default=None, blank=True)
    

class Listing(models.Model):
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_listings", default=None)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="related_listings", default=None)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    image_url = models.URLField(default=None, blank=True)
    highest_bid = models.ForeignKey("Bid", on_delete=models.SET_DEFAULT, null=True, blank=True, default=None)
    start_price = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="won_auction", null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.title} by {self.author}"
    

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_bids", default=None)
    bid_size = models.DecimalField(max_digits=7, decimal_places=2, default=None)
    bid_subject = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids", default=None)

    def __str__(self):
        return f"${self.bid_size} by {self.bidder} on {self.bid_subject}"


class Comment(models.Model):
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", default=None)
    commentator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_comments")
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=1000)
    
    def __str__(self):
        return f"{self.title} by {self.commentator}"


class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.category_name}"
