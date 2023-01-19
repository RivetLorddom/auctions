from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)

class BidAdmin(admin.ModelAdmin):
    list_display = ("bid_subject", "bid_size", "bidder")

admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)
admin.site.register(Category)