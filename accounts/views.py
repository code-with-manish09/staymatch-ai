from copy import error

from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib import auth

#=========register views ===========

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        location = request.POST.get('location')
        contacts = request.POST.get('contacts')
        profile_picture = request.FILES.get('profile_picture')
        email = request.POST.get('email')
        password = request.POST.get('password')

        profile = Profile.objects.create(
            username= username,
            age = age ,
            gender = gender,
            location = location ,
            contacts =contacts,
            profile_picture = profile_picture,
            email=email
        )

        profile.set_password(password)
        profile.save()

        return redirect('login')
    return render(request , ' accounts/register.html')
    

       #==========login views =========== 

def login(request):
    if request.method == 'POST':
         username = request.POST.get('username')
         password = request.POST.get("password")
         user = auth . authenticate(
             username = username ,
             password = password
         )

         if user is  not None :
             auth.login(request , user)
             return redirect('dashboard')
         
         else:
             return render (request, 'accounts/login.html' , {error : 'invalid username or password'})
             