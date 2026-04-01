from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    location = models.CharField(max_length=100, null=True, blank=True)
    contacts = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    profession = models.CharField(max_length=100, default="Software Engineer")
    vibe_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile" if self.user else self.name