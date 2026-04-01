from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib import auth ,messages


def register(request):
    if request.method == 'POST':
        # 1. Data capture
        username = request.POST.get('username')
        full_name = request.POST.get('full_name', '')
        age = request.POST.get('age', '0')
        gender = request.POST.get('gender', '')
        location = request.POST.get('location', '')
        contact = request.POST.get('contact', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        profile_media = request.FILES.get('profile_media')

        # 2. Check existing user
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists!'})

        try:
            # 3. User Create
            new_user = User.objects.create_user(username=username, email=email, password=password)
            user_profile, created = Profile.objects.get_or_create(user=new_user)
            user_profile.name = full_name
            
            # Safe Age Conversion
            if age and str(age).isdigit():
                user_profile.age = int(age)
            
            user_profile.gender = gender
            user_profile.location = location
            user_profile.contacts = contact
            
            if profile_media:
                user_profile.profile_picture = profile_media
                
            user_profile.save()
            
            print(f"--- SUCCESS: {username} registered and profile saved! ---")
            return redirect('login') 

        except Exception as e:
            # Ye lines terminal mein poora sach bol dengi
            import traceback
            traceback.print_exc() 
            return render(request, 'accounts/register.html', {'error': f"Fatal Error: {e}"})

    return render(request, 'accounts/register.html')

from django.shortcuts import render, redirect
from django.contrib import auth, messages

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