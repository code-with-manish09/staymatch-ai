from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from httpx import request
from rooms.models import FlatmateProfile, Listing,Saved_Rooms,Review, SavedFlatmate
from inbox.models import Message
from inbox.views import get_conversations  
from django.contrib.auth.models import User


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

    saved_count = Saved_Rooms.objects.filter(user=request.user).count()
    total_matches = 0

    city_stats = Listing.objects.filter(is_published=True).values('city').annotate(count=Count('id')).order_by('-count')

    total_users = User.objects.count()
    total_listings = Listing.objects.filter(is_published=True).count()

    recent_reviews = Review.objects.select_related('user', 'listing').order_by('-created_at')[:3]
    my_listings = Listing.objects.filter(owner=request.user).prefetch_related('images')

    my_flatmate_profile = FlatmateProfile.objects.filter(user=request.user).first()

    compatible_flatmates = FlatmateProfile.objects.exclude(
    user=request.user
        ).select_related('user').order_by('-created_at')[:6]


    saved_flatmate_ids = list(
    SavedFlatmate.objects.filter(user=request.user).values_list('profile_id', flat=True)
)
    flatmate_inquiries = Message.objects.filter(
    recipient=request.user,
    flatmate_profile__isnull=False,
    is_read=False
).select_related('sender', 'flatmate_profile').order_by('-created_at')[:10]

    
    context = {
        'listings': all_rooms,
        'saved_room_ids': saved_room_ids,
        'user_saved_rooms': user_saved_rooms,
        'recent_messages': recent_messages,
        'unread_count': unread_count,
        'trending_rooms': trending_rooms,
        'saved_count': saved_count,
        'total_matches': total_matches,
        'active_chats': len(recent_messages),
        'city_stats': city_stats,
        'total_users': total_users,
        'total_listings': total_listings,
        'recent_reviews': recent_reviews,
        'my_listings': my_listings,
        'my_listings_available': my_listings.filter(is_published=True).count(),
        'my_total_inquiries': 0, 
        'my_flatmate_posts':  FlatmateProfile.objects.filter(user=request.user),
        'my_flatmate_active':FlatmateProfile.objects.filter(
         user=request.user, is_active=True
        ).count(),
        'my_flatmate_responses': 0,
        'compatible_flatmates': compatible_flatmates,
        'saved_flatmate_ids': saved_flatmate_ids,
        'user_saved_flatmates': SavedFlatmate.objects.filter(user=request.user).select_related('profile'),
        'flatmate_inquiries': flatmate_inquiries,


    }

    return render(request, 'dashboard/dashboard.html', context)

