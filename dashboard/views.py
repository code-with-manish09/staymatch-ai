from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import Profile  # import Profile from accounts app

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