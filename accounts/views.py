from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


def register(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        age       = request.POST.get('age')
        gender    = request.POST.get('gender')
        location  = request.POST.get('location')
        contact   = request.POST.get('contact')
        email     = request.POST.get('email')
        password  = request.POST.get('password')
        
        profile_media = request.FILES.get('profile_media')

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'username already registered!'})

        new_user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password
        )

        Profile.objects.create(
            user=new_user,
            name=full_name,
            age=age,
            gender=gender,
            location=location,
            contact=contact,
            image=profile_media or 'default.jpg'
        )

        return redirect('login')

    return render(request, 'accounts/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password ❌")
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')

@csrf_exempt
@login_required
def dashboard(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None
    return render(request, 'accounts/dashboard.html', {
        'user': user,
        'profile': profile
        })