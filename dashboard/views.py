from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rooms.models import Listing,Saved_Rooms
from inbox.views import get_conversations  

#==========profile===============
def get_user_profile_or_none(user):
    """Return user profile if available, else None."""
    try:
        return user.profile
    except Exception:
        return None
    
    

#==========dashboard view============

from django.db.models import Avg, Count

@login_required(login_url='/login/')
def dashboard(request):
    all_rooms = Listing.objects.filter(is_published=True).order_by('-created_at')

    saved_room_ids = list(
        Saved_Rooms.objects.filter(user=request.user).values_list('room_id', flat=True)
    )
    user_saved_rooms = Saved_Rooms.objects.filter(
        user=request.user
    ).select_related('room')

    all_conversations = get_conversations(request.user)
    recent_messages = all_conversations[:5]
    unread_count = sum(1 for conv in all_conversations if conv['unread'] > 0)

  
    trending_rooms = Listing.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-review_count', '-avg_rating')[:5]

    
    context = {
        'listings': all_rooms,
        'saved_room_ids': saved_room_ids,
        'user_saved_rooms': user_saved_rooms,
        'recent_messages': recent_messages,
        'unread_count': unread_count,
        'trending_rooms': trending_rooms,
    }

    return render(request, 'dashboard/dashboard.html', context)

