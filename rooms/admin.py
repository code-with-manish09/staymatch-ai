from django.contrib import admin
from .models import Amenity, FlatmateProfile, Listing, ListingImage, Review

# Inhe register karne se ye Admin Panel mein dikhne lagenge
admin.site.register(Amenity)
admin.site.register(Listing)
admin.site.register(ListingImage)
admin.site.register(Review)
admin.site.register(FlatmateProfile)
    