from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    try:
        # Login user ki profile uthao
        user_profile = request.user.profile
    except Exception:
        user_profile = None

    context = {'profile': user_profile}
    return render(request, 'dashboard/dashboard.html', context)