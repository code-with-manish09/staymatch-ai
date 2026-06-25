from django.contrib import admin
from .models import OTPVerification, Profile

admin.site.register(Profile)
admin.site.register(OTPVerification)

