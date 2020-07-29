from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing


def index(request):
    listings = Listing.objects.all()
    listings = sorted(listings, key=lambda i: i.created_at, reverse=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
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

@login_required(login_url='/login/')
def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/create_listing.html")
    else:
        title = request.POST["inputTitle"]
        desc = request.POST["inputDesc"]
        bid = request.POST["inputBid"]
        imageurl = request.POST["inputImageurl"]
        category = request.POST["inputCategory"]
        creator = request.user.username
        try:
            newListing = Listing(
                title = title,
                desc = desc,
                bid = bid,
                image = imageurl,
                category = category,
                creator = creator
            )
            newListing.save()
        except:
            return render(request, "auctions/create_listing.html", {
                "message": "Some required fields are not filled."
            })
        return HttpResponseRedirect(reverse("create_listing"))

def listing(request, list_):
    if request.method == "GET":
        return render(request, "auctions/listing.html", {
            "list": Listing.objects.filter(id=list_, active=True)[0]
        })