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
    
    def get_preference_text(self):
        return (
            f"Room type : {self.room_type},"
            f"city: {self.city},"
            f"furnishing : {self.furnishing_status},"
            f"preferred gender : {self.pref_gender},"
            f"preferred occupation: {self.pref_occupation},"
            f"sleep schedule: {self.sleep_schedule},"
            f"cleanliness level : {self.cleanliness_level},"
            f"guest policy : {self.guest_policy},"
            f"wifi included : {self.included_wifi},"
            f"Cooking allowed: {self.included_cooking}, "
            f"House rules: {self.house_rules}, "
            f"Rent: {self.rent}"
        )

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
    
#-----------flatmate post-----------------
class FlatmateProfile(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'), ('Female', 'Female'),
        ('Non-binary', 'Non-binary'), ('Prefer not to say', 'Prefer not to say'),
    ]
    OCCUPATION_CHOICES = [
        ('Student', 'Student'), ('Software / IT', 'Software / IT'),
        ('Corporate Professional', 'Corporate Professional'),
        ('Freelancer', 'Freelancer'), ('Healthcare', 'Healthcare'),
        ('Startup', 'Startup'), ('Research / Academia', 'Research / Academia'),
        ('Creative / Media', 'Creative / Media'), ('Other', 'Other'),
    ]
    CITY_CHOICES = [
        ('Bangalore', 'Bangalore'), ('Mumbai', 'Mumbai'),
        ('Delhi', 'Delhi'), ('Hyderabad', 'Hyderabad'),
        ('Pune', 'Pune'), ('Chennai', 'Chennai'),
        ('Kolkata', 'Kolkata'), ('Patna', 'Patna'),
    ]
    LANGUAGE_CHOICES = [
        ('Hindi', 'Hindi'), ('English', 'English'),
        ('Hindi+English', 'Hindi + English'), ('Any', 'Any'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='flatmate_profile')

    # Step 1
    name           = models.CharField(max_length=120)
    age            = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(45)])
    gender         = models.CharField(max_length=20, choices=GENDER_CHOICES)
    occupation     = models.CharField(max_length=50, choices=OCCUPATION_CHOICES)
    city           = models.CharField(max_length=50, choices=CITY_CHOICES)
    preferred_area = models.CharField(max_length=100, blank=True)
    language_pref  = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, blank=True)
    bio            = models.TextField(max_length=300, blank=True)
    profile_photo  = models.ImageField(upload_to='flatmates/', blank=True, null=True)

    # Step 2
    max_budget     = models.IntegerField(default=12000)
    room_type_pref = models.CharField(max_length=50, default='Any')
    move_in        = models.CharField(max_length=50, default='Flexible')
    stay_duration  = models.CharField(max_length=50, default='Flexible')

    # Step 3
    interest_tags  = models.TextField(blank=True)

    # Step 4
    sleep_schedule     = models.CharField(max_length=50, default='No Preference')
    cleanliness_level  = models.IntegerField(default=7, validators=[MinValueValidator(1), MaxValueValidator(10)])
    noise_tolerance    = models.CharField(max_length=50, default='Moderate OK')
    guest_policy       = models.CharField(max_length=100, default='Occasional OK')
    work_style         = models.CharField(max_length=50, default='Hybrid')
    smoking            = models.CharField(max_length=50, default='Non-smoker')
    alcohol            = models.CharField(max_length=50, default="Don't drink")
    pets               = models.CharField(max_length=50, default='No pets')

    # Step 5
    pref_gender          = models.CharField(max_length=20, default='Any')
    pref_age_range       = models.CharField(max_length=50, default='Any')
    pref_occupation      = models.CharField(max_length=50, default='Any')
    flatmate_expectation = models.TextField(max_length=400, blank=True)

    # Step 6
    contact_phone      = models.CharField(max_length=20)
    contact_email      = models.EmailField()
    contact_preference = models.CharField(max_length=50, default='WhatsApp')
    contact_visibility = models.CharField(max_length=50, default='Show after connect only')

    # Metadata
    vibe_score = models.IntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_tags_list(self):
        import json
        tags = self.interest_tags.strip()
        if not tags:
            return []
        if tags.startswith('['):
            try:
                parsed = json.loads(tags)
                return [str(t).strip().strip('"') for t in parsed if str(t).strip()]
            except Exception:
                pass
        return [t.strip().strip('"') for t in tags.split(',') if t.strip()]
    @property
    def interest_tags_list(self):
        return self.get_tags_list()
            
    def __str__(self):
        return f"{self.name} ({self.city}) — Score: {self.vibe_score}"
    
    def get_preference_text(self):
      return (
        f"Name: {self.name}, Age: {self.age}, Gender: {self.gender}, "
        f"Occupation: {self.occupation}, City: {self.city}, "
        f"Max budget: {self.max_budget}, Room type: {self.room_type_pref}, "
        f"Move-in: {self.move_in}, Sleep schedule: {self.sleep_schedule}, "
        f"Cleanliness: {self.cleanliness_level}/10, "
        f"Noise tolerance: {self.noise_tolerance}, "
        f"Guest policy: {self.guest_policy}, Work style: {self.work_style}, "
        f"Smoking: {self.smoking}, Alcohol: {self.alcohol}, Pets: {self.pets}, "
        f"Language: {self.language_pref}, "
        f"Prefers flatmate gender: {self.pref_gender}, "
        f"Prefers flatmate occupation: {self.pref_occupation}, "
        f"Preferred age range: {self.pref_age_range}, "
        f"Bio: {self.bio}"
    )
    # models.py mein
    @property
    def banner_gradient(self):
        gradients = {
            'Student': 'linear-gradient(135deg,#10B981,#0EA5C9)',
            'Software / IT': 'linear-gradient(135deg,#0EA5C9,#0F1F3D)',
            'Corporate Professional': 'linear-gradient(135deg,#0F1F3D,#1a3260)',
            'Freelancer': 'linear-gradient(135deg,#F59E0B,#EF4444)',
            'Healthcare': 'linear-gradient(135deg,#10B981,#059669)',
            'Startup': 'linear-gradient(135deg,#F59E0B,#0EA5C9)',
            'Research / Academia': 'linear-gradient(135deg,#6366F1,#0F1F3D)',
            'Creative / Media': 'linear-gradient(135deg,#F59E0B,#EF4444)',
        }
        return gradients.get(self.occupation, 'linear-gradient(135deg,#0EA5C9,#0F1F3D)')

    class Meta:
        ordering = ['-vibe_score', '-created_at']


#================saved flatmates====================
class SavedFlatmate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_flatmates')
    profile = models.ForeignKey(FlatmateProfile, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'profile')