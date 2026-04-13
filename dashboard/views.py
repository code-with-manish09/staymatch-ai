from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rooms.models import Listing
from inbox.views import get_conversations  

#==========profile===============
def get_user_profile_or_none(user):
    """Return user profile if available, else None."""
    try:
        return user.profile
    except Exception:
        return None
    
    

#==========dashboard view============


@login_required(login_url='login')
def dashboard(request):
    user_profile = get_user_profile_or_none(request.user)
    listings = Listing.objects.filter(is_published=True).prefetch_related('images').order_by('-created_at')[:6]

    
    recent_messages = get_conversations(request.user)[:5]

    context = {
        'profile': user_profile,
        'listings': listings,
        'recent_messages': recent_messages,  
    }
    return render(request, 'dashboard/dashboard.html', context)