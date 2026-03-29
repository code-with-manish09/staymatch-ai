from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"