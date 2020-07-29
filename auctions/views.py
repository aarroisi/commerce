from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Listing, Watchlist

def index(request):
    listings = Listing.objects.filter(active=True)
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
        creator = request.user
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

def allWL(request, listing_id, active=True):
    if not request.user.is_authenticated:
        return []
    else:
        if active == "NR":
            lists = Listing.objects.filter(id=listing_id)[0]
        else:
            lists = Listing.objects.filter(id=listing_id, active=active)[0]
        wls = Watchlist.objects.filter(
            creator = request.user,
            listing = lists,
        )
        return wls

def listing(request, listing_id):
    wls = allWL(request, listing_id, active="NR")
    if len(wls) == 0:
        not_added = True
    else:
        not_added = False
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.filter(id=listing_id)[0],
        "not_added": not_added,
    })

@login_required(login_url='/login/')
def addwl(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        wls = allWL(request, listing_id)
        if len(wls) == 0:
            newWL = Watchlist(
                creator = request.user,
                listing = Listing.objects.filter(id=listing_id, active=True)[0],
            )
            newWL.save()
        else:
            messages.warning(request, 'Already in the wathchlist.')
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        messages.success(request, 'Added to watchlist.')
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login/')
def rmwl(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        wls = allWL(request, listing_id)
        wls.delete()
        messages.error(request, 'Removed from the watchlist.')
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login/')
def watchlist(request):
    wls = Watchlist.objects.filter(creator=request.user)
    wls_id = [i.listing.id for i in wls]
    listings = Listing.objects.filter(pk__in=wls_id)
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })

@login_required(login_url='/login/')
def new_bid(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        bid = int(request.POST["bid"])
        listing = Listing.objects.get(id=listing_id, active=True)
        old_bid = int(listing.bid)
        if request.user != Listing.objects.get(id=listing_id).creator:
            if bid > old_bid :
                listing.bid = bid
                listing.last_bidder = request.user
                listing.save()
                HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
            else:
                messages.error(request, 'New bid is too low.')
                return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        else:
            messages.error(request, 'You are not allowed to make self-bidding.')
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        messages.success(request, 'New bid accepted.')
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login/')
def close(request):
    pass