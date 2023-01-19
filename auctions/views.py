from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment


class NewListingForm(forms.Form):
    CHOICES = [(x.category_name, x.category_name) for x in Category.objects.all()]
        
    title = forms.CharField(label="New Listing Title")
    description = forms.CharField(label="Description", widget=forms.Textarea)
    starting_bid = forms.IntegerField(label="Starting price ($)")
    image_url = forms.URLField(label="Image URL (optional)", required=False)
    category = forms.ChoiceField(label="Category", choices=CHOICES, initial="Unspecified", required=False)


class NewBid(forms.Form):
    bid_size = forms.DecimalField(label="Your bid", max_digits=9, decimal_places=2, max_value=99999.99)


class CommentForm(forms.Form):
    title = forms.CharField(label="Title:")
    comment_body = forms.CharField(label="Comment:", widget=forms.Textarea)


def index(request):
    all_active_listings = Listing.objects.filter(active=True)
    for listing in all_active_listings:
        
        listing_bids = Bid.objects.filter(bid_subject=listing)
        try:
            listing.highest_bid = listing_bids.order_by('-bid_size')[0]
        except:
            pass
        listing.save()
    return render(request, "auctions/index.html", {
        "listings": all_active_listings,
    })


def listing_page(request, listing_title):
    bidding_error = ''
    error_flag = False
    listing = Listing.objects.get(title = listing_title)
    listing_bids = Bid.objects.filter(bid_subject=listing)
    try:
        listing.highest_bid = listing_bids.order_by('-bid_size')[0]
        current_winner = listing.highest_bid.bidder
    except:
        current_winner = None
    listing.save()

    if request.user.is_authenticated:
        current_watchlist = request.user.watchlist.all()
    else:
        current_watchlist = None

    if request.method == "POST":
        if "add_delete" in request.POST:
            if request.POST["add_delete"] == "Add to Watchlist":
                request.user.watchlist.add(listing)
            else:
                request.user.watchlist.remove(listing)

        if "close_auction" in request.POST:
            listing.active = False
            listing.winner = current_winner
            listing.save()

        if "submit_bid" in request.POST:
            form = NewBid(request.POST)
            if listing.highest_bid:
                if float(request.POST["bid_size"]) <= listing.highest_bid.bid_size or float(request.POST["bid_size"]) <= listing.start_price:
                    bidding_error = "YOUR BID WAS NOT ACCEPTED! You must bid higher than the current price!"
                    error_flag = True
            if form.is_valid() and not error_flag:
                new_bid = Bid()
                new_bid.bidder = request.user
                new_bid.bid_size = form.cleaned_data["bid_size"]
                new_bid.bid_subject = listing
                new_bid.save()
                return HttpResponseRedirect(reverse("listing_page", args=(listing.title, ),))

        if "add_comment" in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = Comment()
                new_comment.auction = listing
                new_comment.commentator = request.user
                new_comment.title = form.cleaned_data["title"]
                new_comment.text = form.cleaned_data["comment_body"]
                new_comment.save()
                return HttpResponseRedirect(reverse("listing_page", args=(listing.title, )))
                
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_watchlist": current_watchlist,
        "bid_form": NewBid(),
        "comment_form": CommentForm(),
        "bidding_error": bidding_error,
        "comments": Comment.objects.filter(auction=listing)[::-1],
        "current_bid": listing.highest_bid,
        "winner": current_winner
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def this_category(request, category_name):
    category = Category.objects.get(category_name=category_name)
    active_listings = Listing.objects.filter(category=category, active=True)

    for listing in active_listings:
        listing_bids = Bid.objects.filter(bid_subject=listing)
        try:
            listing.highest_bid = listing_bids.order_by('-bid_size')[0]
        except:
            pass
        listing.save()

    return render(request, "auctions/this_category.html", {
        "categories": Category.objects.all(),
        "listings": active_listings,
        "category_name": category_name
    })

@login_required(login_url='login')
def watchlist(request):
    user_watchlist = request.user.watchlist.all()
    for listing in user_watchlist:
        listing_bids = Bid.objects.filter(bid_subject=listing)
        try:
            listing.highest_bid = listing_bids.order_by('-bid_size')[0]
        except:
            pass
        listing.save()
    return render(request, "auctions/watchlist.html", {
        "listings": user_watchlist
    })


@login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            new_listing = Listing()
            new_listing.author = request.user
            new_listing.title = form.cleaned_data["title"]
            new_listing.description = form.cleaned_data["description"]
            new_listing.start_price = form.cleaned_data["starting_bid"]
            new_listing.image_url = form.cleaned_data["image_url"]
            new_listing.category = Category.objects.get(category_name = form.cleaned_data["category"])
            new_listing.save()
            return redirect("/")

    return render(request, "auctions/create_listing.html", {
        "form": NewListingForm()
    })
