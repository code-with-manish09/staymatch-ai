from django.db import models
from django.contrib.auth.models import User

#==========profile model ===========

class Profile(User):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES , null=True , blank= True)
    location = models.CharField(max_length=100)
    contacts = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to = 'profile_pictures/' , null = True , blank= True)
    def __str__(self):
        return self.username
