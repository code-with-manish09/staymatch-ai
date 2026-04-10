from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rooms.models import Listing


def get_user_profile_or_none(user):
    """Return user profile if available, else None."""
    try:
        return user.profile
    except Exception:
        return None


@login_required(login_url='login')
def dashboard(request):
    # Login user ka profile (agar ho)
    user_profile = get_user_profile_or_none(request.user)

    # Latest published listings show karne ke liye
    listings = Listing.objects.filter(is_published=True).prefetch_related('images').order_by('-created_at')[:6]

    context = {'profile': user_profile, 'listings': listings}
    return render(request, 'dashboard/dashboard.html', context)