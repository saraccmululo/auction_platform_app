from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Category, Listing, Comment, Bid


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    all_categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": active_listings,
        "categories": all_categories
    })

def category_page(request):
    if request.method== 'POST':
        selected_category_id=request.POST.get("category")
        category_obj=Category.objects.get(id=selected_category_id)
        listings = Listing.objects.filter(is_active=True, category=category_obj)
        
        all_categories = Category.objects.all()

        return render(request, "auctions/category_page.html", {
        "listings": listings,
        "category": category_obj,
        "categories": all_categories
        })
    return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login')
def create_listing(request):
    if request.method == "POST":
        #getting the form data
        title = request.POST.get("title").strip()
        description = request.POST.get("description").strip()
        image_url = request.POST.get("image_url")
        start_bid_str = request.POST.get("start_bid")
        category_id = request.POST.get("category")
        current_user = request.user #gets the user who wants to add the listing

        #Validation for title, description and bid:
        if not title:
            messages.error(request,"Title is required")
        if not description:
            messages.error(request,"Description is required")
        if not start_bid_str:
            messages.error(request, "Starting bid is required")
        else: 
            try:
                start_bid=Decimal(start_bid_str)
                if start_bid <= 0:
                    messages.error(request, "Starting bid must be greater than zero.")
            except (InvalidOperation, TypeError):
                messages.error(request, "Starting bid must be a valid number.")

        if messages.get_messages(request):
            return redirect("create")

        # getting the category name:
        category = Category.objects.get(id=category_id) if category_id else None

        #creating a new listing object with that data
        Listing.objects.create(
            title=title,
            description=description,
            image_url=image_url,
            start_bid=Decimal(start_bid),
            category=category,
            owner=current_user,
        )
        return redirect("index")
    
    # If GET request → show form
    all_categories = Category.objects.all()
    return render(request, "auctions/create.html", {
        "categories": all_categories
    })


def listing(request, listing_id):
    listing_obj = Listing.objects.get(id =listing_id)
    #Watchlist button logic
    if request.user.is_authenticated:
        if listing_obj in request.user.watchlist.all():
            message = "Remove from watchlist"
        else:
            message= "Add to watchlist"

    #Display list of comments
    comments=Comment.objects.filter(listing=listing_obj).order_by("-timestamp")

    #Display highest bid
    highest_bid_obj= Bid.objects.filter(listing=listing_obj).order_by("-amount").first()

    if not highest_bid_obj:
        highest_bid_amount=listing_obj.start_bid 
    else:
        highest_bid_amount=highest_bid_obj.amount

    return render (request, "auctions/listing.html", {
        "listing": listing_obj,
        "message": message,
        "comments": comments,
        "highest_bid": highest_bid_amount,
        "winner": listing_obj.winner
    })

@login_required(login_url='/login')
def watchlist_toggle(request, listing_id):
    listing_obj= Listing.objects.get(id=listing_id)
    if listing_obj in request.user.watchlist.all():
        request.user.watchlist.remove(listing_obj)
        message= "Add to watchlist"

    else:
        request.user.watchlist.add(listing_obj)
        message= "Remove from watchlist"
        
    return render (request, "auctions/listing.html", {
            "listing": listing_obj,
            "message": message
        })

@login_required(login_url='/login')
def watchlist(request):
    watchlist_listings = request.user.watchlist.all()
    all_categories = Category.objects.all()
    return render(request, "auctions/watchlist.html", {
        "listings": watchlist_listings,
        "categories": all_categories
    })

@login_required(login_url='/login')
def place_bid(request, listing_id):
    #get data from form and the listing id
    if request.method=="POST":
        bid_amount_str=request.POST.get("bid_amount")
        listing_obj=Listing.objects.get(id=listing_id)

        # get current highest bid, default to start_bid if no bids yet
        highest_bid_obj= Bid.objects.filter(listing=listing_obj).order_by("-amount").first()

        if not highest_bid_obj:
           highest_bid_amount=listing_obj.start_bid 
        else:
            highest_bid_amount=highest_bid_obj.amount

        # validation
        if not bid_amount_str:
            messages.error(request, "Bid cannot be empty",extra_tags="bid")
        else: 
            try:
                bid_amount=Decimal(bid_amount_str)
                if bid_amount <= highest_bid_amount:
                    messages.error(request, f"Bid must be greater than the current highest bid (${highest_bid_amount:.2f})", extra_tags="bid")
                else:
                    #saving valid bid to db
                    Bid.objects.create(
                        user=request.user,
                        listing=listing_obj,
                        amount=bid_amount
                    )
                    messages.success(request, "Your bid was placed successfully!", extra_tags="bid")
            except (InvalidOperation, TypeError):
                messages.error(request, "Bid must be a valid number.", extra_tags="bid")

    return redirect("listing", listing_id=listing_id)

@login_required(login_url='/login')
def add_comment(request, listing_id):
    if request.method=="POST":
    #get the comment from form and listing obj and user obj related to that comment
        comment_to_add= request.POST.get("add_comment").strip()
        listing_obj= Listing.objects.get(id=listing_id)

        # validation
        if not comment_to_add:
            messages.error(request, "Comment cannot be empty", extra_tags="comment")
    
        #saving comment to db
        Comment.objects.create(
            user= request.user,
            listing=listing_obj,
            text=comment_to_add,
        )
    return redirect("listing", listing_id=listing_id)
    
def close_listing(request, listing_id):
    listing_obj=Listing.objects.get(id=listing_id)
    if request.user != listing_obj.owner:
        messages.error(request, "Only the owner can close this listing.",extra_tags="close_listing")
        return redirect("listing", listing_id=listing_id)
    
    listing_obj.is_active = False

    highest_bid=Bid.objects.filter(listing=listing_obj).order_by("-amount").first()

    if highest_bid:
        listing_obj.winner = highest_bid.user
    # Save the listing changes into db
    listing_obj.save()
    
    messages.success(request, "You closed this auction successfully. This listing has been deactivated.", extra_tags="close_listing")

    return redirect('listing', listing_id=listing_id)

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

