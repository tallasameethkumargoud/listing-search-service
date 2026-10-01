from django.urls import path
from .views import search_listings

urlpatterns = [
    path("listings/", search_listings, name="search-listings"),
]