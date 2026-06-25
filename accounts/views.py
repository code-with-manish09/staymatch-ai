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
import random
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from .models import Profile, OTPVerification


#========================== OTP GENERATION FUNCTION ==========================
# 1. Logger setup 
logger = logging.getLogger(__name__)
def generate_otp():
    return str(random.randint(100000, 999999))


#=========================otp verification view=========================

def verify_otp(request):
    if 'pending_user' not in request.session:
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        email = request.session['pending_user']['email']

        try:
            otp_obj = OTPVerification.objects.filter(
                email=email,
                is_used=False
            ).latest('created_at')
        except OTPVerification.DoesNotExist:
            messages.error(request, 'OTP expired. Register again.')
            return redirect('register')

        if otp_obj.is_expired():
            messages.error(request, 'OTP expired. Register again.')
            otp_obj.delete()
            return redirect('register')

        if otp_obj.otp != entered_otp:
            messages.error(request, 'Wrong OTP. Try again.')
            return render(request, 'accounts/verify_otp.html')

        # OTP sahi hai — ab user banao
        otp_obj.is_used = True
        otp_obj.save()

        data = request.session['pending_user']

        try:
            new_user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            full_name = data.get('full_name', '')
            if full_name:
                names = full_name.split(' ')
                new_user.first_name = names[0]
                new_user.last_name = " ".join(names[1:]) if len(names) > 1 else ''
                new_user.save()

            user_profile, _ = Profile.objects.get_or_create(user=new_user)
            user_profile.full_name = full_name
            if data['age'] and str(data['age']).isdigit():
                user_profile.age = int(data['age'])
            user_profile.gender = data['gender']
            user_profile.location = data['location']
            user_profile.contacts = data['contact']

            # Profile picture restore 
            if 'pending_pic' in request.session:
                import base64
                from django.core.files.base import ContentFile
                pic = request.session['pending_pic']
                pic_data = base64.b64decode(pic['data'])
                user_profile.profile_picture.save(
                    pic['name'],
                    ContentFile(pic_data),
                    save=False
                )
                del request.session['pending_pic']

            user_profile.save()

            # cleanup session data
            del request.session['pending_user']

            messages.success(request, f"Account created! Welcome {data['username']} 🎉")
            return redirect('login')

        except Exception as e:
            logger.exception("User creation failed after OTP: %s", e)
            messages.error(request, 'Something went wrong. Try again.')
            return redirect('register')

    return render(request, 'accounts/verify_otp.html')


#=========================resend otp view=========================
@require_POST
def resend_otp(request):
    if 'pending_user' not in request.session:
        return JsonResponse({'status': 'error'}, status=400)

    email = request.session['pending_user']['email']
    otp = generate_otp()
    OTPVerification.objects.filter(email=email).delete()
    OTPVerification.objects.create(email=email, otp=otp)

    try:
        send_mail(
            subject='🔐 Your StayMatch OTP (Resent)',
            message=f'Your new OTP is: {otp}\n\nValid for 2 minutes only.\n\n— StayMatch Team',
            from_email=None,
            recipient_list=[email],
        )
        return JsonResponse({'status': 'sent'})
    except Exception as e:
        logger.exception("Resend OTP failed: %s", e)
        return JsonResponse({'status': 'error'}, status=500)

#======================Register view=========================


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email', '')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        full_name = request.POST.get('full_name', '')
        age       = request.POST.get('age', '0')
        gender    = request.POST.get('gender', '')
        location  = request.POST.get('location', '')
        contact   = request.POST.get('contact', '')
        profile_picture = request.FILES.get('profile_picture')

        # Basic validations
        if not username or not password:
            messages.error(request, 'Username and password required.')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        # Session mein data save karo — user abhi mat banao
        request.session['pending_user'] = {
            'username': username,
            'email': email,
            'password': password,
            'full_name': full_name,
            'age': age,
            'gender': gender,
            'location': location,
            'contact': contact,
        }

        # Profile picture session mein nahi ja sakti — file handle alag karenge
        if profile_picture:
            import base64
            request.session['pending_pic'] = {
                'name': profile_picture.name,
                'data': base64.b64encode(profile_picture.read()).decode('utf-8'),
                'content_type': profile_picture.content_type,
            }

        # OTP banao aur bhejo
        otp = generate_otp()
        OTPVerification.objects.filter(email=email).delete()  # Pehle wale OTPs delete karo
        OTPVerification.objects.create(email=email, otp=otp)

        try:
            send_mail(
                subject='🔐 Your StayMatch OTP',
                message=f'Your OTP is: {otp}\n\nValid for 2 minutes only.\n\n— StayMatch Team',
                from_email=None,  # settings 
                recipient_list=[email],
            )
        except Exception as e:
            logger.exception("OTP email failed: %s", e)
            messages.error(request, 'Email sending failed.')
            return redirect('register')

        return redirect('verify_otp')

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
            return redirect('login')

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