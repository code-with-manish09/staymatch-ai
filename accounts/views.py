from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib import auth ,messages

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
        
        # Photo/Video ke liye request.FILES zaroori hai
        profile_media = request.FILES.get('profile_media')

        # 2. Check karo agar User pehle se exists karta hai
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'username already registered!'})

        # 3. Pehle Django ka Official 'User' banao (Security ke liye create_user zaroori hai)
        # User create
        new_user = User.objects.create_user(
        username=username, 
        email=email, 
        password=password
     )

# Profile create (correct)
        Profile.objects.create(
        user=new_user,
        name=full_name,
        age=age,
       gender=gender,
       location=location,
       contacts=contact,
       profile_picture=profile_media
   )
        print(f"Mubarak ho! {full_name} ka data save ho gaya.")
        return redirect('login') # Registration ke baad Login page par bhej do

    return render(request, 'accounts/register.html')
       #==========login views =========== 


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