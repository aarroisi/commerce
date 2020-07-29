from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Listing, Watchlist, Bid
from django.utils import timezone


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
        starting_bid = request.POST["inputBid"]
        imageurl = request.POST["inputImageurl"]
        category = request.POST["inputCategory"]
        creator = request.user
        try:
            newListing = Listing(
                title = title,
                desc = desc,
                starting_bid = starting_bid,
                image = imageurl,
                category = category,
                creator = creator,
                current_bid = starting_bid,
            )
            newListing.save()
        except:
            messages.error(request, 'Some required fields are not filled.')
            return HttpResponseRedirect(reverse("create_listing"))
        
        messages.success(request, 'New listing is added.')
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": newListing.id}))

def allWL(request, listing_id, active=True, active2=True):
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
            active = active2,
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
        wls = allWL(request, listing_id, active2=False)
        if len(wls) == 0:
            newWL = Watchlist(
                creator = request.user,
                listing = Listing.objects.filter(id=listing_id, active=True)[0],
            )
            newWL.save()
        elif len([i for i in wls if i.active == False]) > 0:
            exsWL = wls[0]
            exsWL.active = True
            exsWL.save()
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
        wls = allWL(request, listing_id)[0]
        wls.active = False
        wls.save()
        messages.warning(request, 'Removed from the watchlist.')
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login/')
def watchlist(request):
    wls = Watchlist.objects.filter(creator=request.user, active=True)
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
        if listing.current_bid:
            old_bid = int(listing.current_bid)
        else:
            old_bid = int(listing.starting_bid)
        
        if request.user != Listing.objects.get(id=listing_id).creator:
            if Listing.objects.get(id=listing_id).last_bidder:
                if bid > old_bid:
                    listing.current_bid = bid
                    listing.last_bidder = request.user
                    bid_new = Bid(
                        creator = request.user,
                        listing = listing,
                        new_bid = bid
                    )
                    listing.save()
                    bid_new.save()
                else:
                    messages.error(request, 'New bid is too low.')
                    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
            else:
                if bid >= old_bid:
                    listing.current_bid = bid
                    listing.last_bidder = request.user
                    bid_new = Bid(
                        creator = request.user,
                        listing = listing,
                        new_bid = bid
                    )
                    listing.save()
                    bid_new.save()
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
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id, active=True)
        if request.user == Listing.objects.get(id=listing_id).creator:
            listing.active = False
            wls = Watchlist.objects.filter(listing=listing)
            listing.save()
            for i in wls:
                i.delete()
        else:
            messages.error(request, 'You are not authorized to close this listing.')
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        messages.success(request, 'You close this listing.')
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login/')
def won(request):
    listings = Listing.objects.filter(active=False, last_bidder=request.user)
    listings = sorted(listings, key=lambda i: i.created_at, reverse=True)
    return render(request, "auctions/won.html", {
        "listings": listings,
    })

def categories(request):
    listings = Listing.objects.filter(active=True)
    catgs = [i.category for i in listings if i.category != ""]
    catgs = list(set(catgs))
    return render(request, "auctions/categories.html", {
        "catgs": catgs,
    })

def category(request, catg):
    listings = Listing.objects.filter(active=True, category=catg)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "catg": catg,
    })

def my_listings(request):
    listings = Listing.objects.filter(creator=request.user)
    return render(request, "auctions/my_listings.html", {
        "listings": listings,
    })