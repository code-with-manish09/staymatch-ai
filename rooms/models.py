from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Amenity(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=20, help_text="Emoji ya Icon class")

    def __str__(self):
        return self.name

class Listing(models.Model):
    # 1. Basics & User Relationship
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    
    # Choices for Dropdowns
    CITY_CHOICES = [
        ('Bangalore', 'Bangalore'), ('Mumbai', 'Mumbai'), 
        ('Delhi', 'Delhi'), ('Patna', 'Patna') # Add more
    ]
    ROOM_TYPES = [
        ('Private Room', 'Private Room'), ('Shared Room', 'Shared Room'),
        ('Studio', 'Studio / 1BHK'), ('Master Bedroom', 'Master Bedroom')
    ]
    
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    area = models.CharField(max_length=100)
    address = models.TextField()
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES)
    bhk_config = models.CharField(max_length=20, default="1 BHK")
    floor = models.CharField(max_length=50)
    available_from = models.DateField()
    min_stay = models.CharField(max_length=50)

    # 2. Pricing
    rent = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(80000)])
    deposit = models.CharField(max_length=50)
    maintenance = models.CharField(max_length=50)
    included_wifi = models.BooleanField(default=False)
    included_electricity = models.BooleanField(default=False)
    included_water = models.BooleanField(default=False)
    included_gas = models.BooleanField(default=False)
    included_cooking = models.BooleanField(default=False)
    included_housekeeping = models.BooleanField(default=False)
    
    # 3. Amenities & Furnishing
    FURNISH_CHOICES = [
        ('Fully', 'Fully Furnished'), ('Semi', 'Semi Furnished'), ('Unfurnished', 'Unfurnished')
    ]
    furnishing_status = models.CharField(max_length=20, choices=FURNISH_CHOICES)
    amenities = models.ManyToManyField(Amenity, blank=True)

    # 4. Description & Rules
    description = models.TextField(max_length=400)
    house_rules = models.TextField(blank=True)
    nearest_metro = models.CharField(max_length=100, blank=True)
    distance_to_hub = models.CharField(max_length=100, blank=True)

    # 5. Flatmate Preferences (For AI Matching)
    GENDER_PREF = [('Any', 'Any'), ('Male', 'Male only'), ('Female', 'Female only')]
    pref_gender = models.CharField(max_length=10, choices=GENDER_PREF, default='Any')
    pref_occupation = models.CharField(max_length=50, default='Any')
    sleep_schedule = models.CharField(max_length=50, default='No preference')
    cleanliness_level = models.IntegerField(default=7, validators=[MinValueValidator(1), MaxValueValidator(10)])
    guest_policy = models.CharField(max_length=100, default='Occasional guests OK')

    # Metadata
    is_published = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=120, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.city}"

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/')

    
    #=========saved rooms ===========


class Saved_Rooms(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_rooms')
    room = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True) # DateField ki jagah DateTime behtar hai

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user.username} saved {self.room.title}"
    
    #================reviews====================    

class Review(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    cleanliness_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    location_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    value_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    host_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('listing', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.listing.title} ({self.rating}★)"