from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def dashboard(request):
     return render(request, 'dashboard/dashboard.html')
def update_profile(request):
    return render(request, 'dashboard/updateprofile.html')

@login_required
def dashboard(request):
    profile = request.user.profile   # 🔥 get logged-in user data

    return render(request, 'dashboard/dashboard.html', {
        'profile': profile
    })