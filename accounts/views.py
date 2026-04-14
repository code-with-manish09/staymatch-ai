import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout   
from django.http import JsonResponse


# 1. Logger setup (Professional error tracking ke liye)
logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        # Data Capture
        username = request.POST.get('username')
        email    = request.POST.get('email', '')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name', '')
        age       = request.POST.get('age', '0')
        gender    = request.POST.get('gender', '')
        location  = request.POST.get('location', '')
        contact   = request.POST.get('contact', '')
        profile_picture = request.FILES.get('profile_picture')

        # 2. Input Validation (Security check)
        if not username or not password:
            return render(request, 'accounts/register.html', {
                'error': 'Username and password are required.'
            })

        # 3. Check existing user
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Username already exists!'
            })

        try:
            # 4. User Create
            new_user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password
            )
            
            # 5. Profile Handle (Signal-safe 'get_or_create')
            user_profile, created = Profile.objects.get_or_create(user=new_user)
            
            # Data Fill
            user_profile.full_name = full_name
            if age and str(age).isdigit():
                user_profile.age = int(age)
            
            user_profile.gender = gender
            user_profile.location = location
            user_profile.contacts = contact
            
            if profile_picture:
                user_profile.profile_picture = profile_picture
                
            user_profile.save()
            
            # 6. Success Logic
            messages.success(request, f"Account created for {username}!")
            return redirect('login') 

        except Exception as e:
            # 7. Logging (Terminal mein poora traceback dikhega, par user ko nahi)
            logger.exception("Registration failed for user: %s", username)
            
            # User ko sirf generic message dikhao (Cybersecurity safety)
            return render(request, 'accounts/register.html', {
                'error': "Registration failed due to a system error. Please try again."
            })

    # GET Request
    return render(request, 'accounts/register.html')



#-------------------------- LOGIN VIEW -----------------------------------
 
def login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login successful 🚀")
            return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password ❌")
            return redirect('login')   # 🔥 IMPORTANT CHANGE

    return render(request, 'accounts/login.html')



#-------------------------- UPDATE PROFILE VIEW -----------------------------------
@login_required
def update_profile(request):
    # 1. 'get_or_create' use karo taaki 'Profile Not Found' kabhi na aaye
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # 2. Data Capture (Make sure name matches your HTML)
        full_name = request.POST.get('full_name', '').strip()
        email     = request.POST.get('email')
        age       = request.POST.get('age')
        gender    = request.POST.get('gender')
        location  = request.POST.get('location')
        contact   = request.POST.get('contact')
        profile_picture = request.FILES.get('profile_picture') # HTML input name
        if gender:
            gender = gender.title()

        # 3. Update User Model
        if email:
            request.user.email = email
        
        if full_name:
             names = full_name.split(' ')
             request.user.first_name = names[0]
             if len(names) > 1:
                 request.user.last_name = " ".join(names[1:])
             else:
                 request.user.last_name = "" # Clear last name if only one name given
        
        request.user.save()

        # 4. Update Profile Model
        if full_name:
            user_profile.full_name = full_name
        if age and str(age).isdigit():
            user_profile.age = int(age)
            
        user_profile.gender = gender
        user_profile.location = location
        user_profile.contacts = contact
        
        if profile_picture :
            user_profile.profile_picture = profile_picture
            
        user_profile.save()

        messages.success(request, 'Profile updated successfully! ✨')
        return redirect('dashboard')

    # 5. GET Request
    context = {
        'profile': user_profile,
        'user': request.user
    }
    return render(request, 'accounts/update_profile.html', context)



#-------------------------- LOGOUT VIEW ----------------------------------- 
@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, "You have been logged out. See you soon! 👋")
    return redirect('login')



#===============Tags views =====================

import json
from django.http import JsonResponse
from .models import Profile # Apna model import check kar lena

def save_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tags = data.get('tags', [])
            score = data.get('score', 0)

            # 🔥 CHANGE YAHAN HAI: 
            # Agar profile nahi hai, toh ye line use create kar degi
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            profile.personality_tags = tags
            profile.vibe_score = score
            profile.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'invalid request'}, status=400)