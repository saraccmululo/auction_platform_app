from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("category_page", views.category_page, name="category_page"),
    path("listing<int:listing_id>/", views.listing, name="listing"),
    path("listing<int:listing_id>/watchlist_toggle", views.watchlist_toggle, name="watchlist_toggle"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("listing<int:listing_id>/add_comment/", views.add_comment, name="add_comment"),
    path("listing<int:listing_id>/place_bid/", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/close", views.close_listing, name="close_listing")
]
