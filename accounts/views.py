import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout   


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
        profile_media = request.FILES.get('profile_media')

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
            user_profile.name = full_name
            if age and str(age).isdigit():
                user_profile.age = int(age)
            
            user_profile.gender = gender
            user_profile.location = location
            user_profile.contacts = contact
            
            if profile_media:
                user_profile.profile_picture = profile_media
                
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

#-------------------------- LOGOUT VIEW ----------------------------------- 
@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, "You have been logged out. See you soon! 👋")
    return redirect('login')