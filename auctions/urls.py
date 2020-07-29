from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>/", views.listing, name="listing"),
    path("addwl/", views.addwl, name="addwl"),
    path("rmwl/", views.rmwl, name="rmwl"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("new_bid/", views.new_bid, name="new_bid"),
    path("close/", views.close, name="close"),
    path("won/", views.won, name="won"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:catg>/", views.category, name="category"),
    path("my_listings/", views.my_listings, name="my_listings"),
]

