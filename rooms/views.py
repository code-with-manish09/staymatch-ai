from datetime import date
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Listing, Amenity, ListingImage, Review
from django.http import JsonResponse  # already hai
from rooms.services.services import get_vibe_score  # yahan add karo
# Utility functions


def to_int(value, default):
    """Safely convert string to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
    


#===============amenities====================

def build_included_flags(selected_items):
    """Convert selected included-items list to DB boolean flags."""
    return {
        'included_wifi': 'WiFi' in selected_items,
        'included_electricity': 'Electricity' in selected_items,
        'included_water': 'Water' in selected_items,
        'included_gas': 'Gas' in selected_items,
        'included_cooking': 'Cooking' in selected_items,
        'included_housekeeping': 'Housekeeping' in selected_items,
    }

#===============post room====================

@login_required 
def post_room(request):
    if request.method == 'POST':
        # Basic fields
        title = request.POST.get('title') or 'Untitled Listing'
        city = request.POST.get('city') or 'Bangalore'
        area = request.POST.get('area') or 'Not specified'
        room_type = request.POST.get('room_type') or 'Private Room'
        description = request.POST.get('description') or ''
        rent = to_int(request.POST.get('rent') or 12000, 12000)

        available_from = request.POST.get('available_from') or date.today()
        selected_included = request.POST.getlist('included_items')
        included_flags = build_included_flags(selected_included)

        # Create listing
        new_listing = Listing.objects.create(
            owner=request.user,
            title=title,
            city=city,
            area=area,
            address=request.POST.get('address') or 'Address not provided',
            room_type=room_type,
            bhk_config=request.POST.get('bhk_config') or '1 BHK',
            floor=request.POST.get('floor') or 'Not specified',
            rent=rent,
            available_from=available_from,
            min_stay=request.POST.get('min_stay') or '1 month',
            deposit=request.POST.get('deposit') or '1 month rent',
            maintenance=request.POST.get('maintenance') or 'Included in rent',
            included_wifi=included_flags['included_wifi'],
            included_electricity=included_flags['included_electricity'],
            included_water=included_flags['included_water'],
            included_gas=included_flags['included_gas'],
            included_cooking=included_flags['included_cooking'],
            included_housekeeping=included_flags['included_housekeeping'],
            furnishing_status=request.POST.get('furnishing_status') or 'Fully',
            description=description,
            house_rules=request.POST.get('house_rules') or '',
            nearest_metro=request.POST.get('nearest_metro') or '',
            distance_to_hub=request.POST.get('distance_to_hub') or '',
            pref_gender=request.POST.get('pref_gender') or 'Any',
            pref_occupation=request.POST.get('pref_occupation') or 'Any',
            sleep_schedule=request.POST.get('sleep_schedule') or 'No preference',
            cleanliness_level=request.POST.get('cleanliness_level') or 7,
            guest_policy=request.POST.get('guest_policy') or 'Occasional guests OK',
            is_published=True,
            contact_name=request.POST.get('contact_name') or request.user.get_full_name() or request.user.username,
            contact_phone=request.POST.get('contact_phone') or '',
            contact_email=request.POST.get('contact_email') or request.user.email or '',
        )

        # Save selected amenities
        selected_amenities = request.POST.getlist('amenities')
        for ame_name in selected_amenities:
            amenity_obj, _ = Amenity.objects.get_or_create(
                name=ame_name,
                defaults={'icon': '✨'}
            )
            new_listing.amenities.add(amenity_obj)

        # Save uploaded images
        images = request.FILES.getlist('images')
        if not images:
            images = request.FILES.getlist('images[]')
        for img in images:
            ListingImage.objects.create(listing=new_listing, image=img)

        return redirect('dashboard')

    return render(request, 'rooms/post_room.html')

#==============room details====================
from django.db.models import Avg
from django.shortcuts import render

def room_details(request, room_id=None):
    qs = Listing.objects.prefetch_related('amenities', 'images')

    room = qs.filter(id=room_id).first() if room_id else qs.order_by('-created_at').first()

    included = {
        'wifi': room.included_wifi if room else False,
        'electricity': room.included_electricity if room else False,
        'water': room.included_water if room else False,
        'gas': room.included_gas if room else False,
        'cooking': room.included_cooking if room else False,
        'housekeeping': room.included_housekeeping if room else False,
    }

    # ✅ Already reviewed check (unchanged)
    already_reviewed = False
    if request.user.is_authenticated and room:
        already_reviewed = Review.objects.filter(listing=room, user=request.user).exists()

    # ✅ Reviews queryset (safe if room None)
    reviews = Review.objects.filter(listing=room).order_by('-created_at') if room else Review.objects.none()
    total_reviews = reviews.count()

    # ✅ Aggregate once (optimized)
    averages = reviews.aggregate(
        avg_rating=Avg('rating'),
        avg_cleanliness=Avg('cleanliness_rating'),
        avg_location=Avg('location_rating'),
        avg_value=Avg('value_rating'),
        avg_host=Avg('host_rating'),
    )

    # ✅ Clean + safe values
    avg_rating = round(averages['avg_rating'], 1) if averages['avg_rating'] else None

    avg_cleanliness = round(averages['avg_cleanliness'], 1) if averages['avg_cleanliness'] else 0
    avg_location = round(averages['avg_location'], 1) if averages['avg_location'] else 0
    avg_value = round(averages['avg_value'], 1) if averages['avg_value'] else 0
    avg_host = round(averages['avg_host'], 1) if averages['avg_host'] else 0

    # ✅ ⭐ IMPORTANT FIX: percentage conversion (UI bars ke liye)
    avg_cleanliness_percent = avg_cleanliness * 20
    avg_location_percent = avg_location * 20
    avg_value_percent = avg_value * 20
    avg_host_percent = avg_host * 20

    context = {
        'room': room,
        'included': included,
        'already_reviewed': already_reviewed,

        # ratings (numbers)
        'avg_rating': avg_rating,
        'avg_cleanliness': avg_cleanliness,
        'avg_location': avg_location,
        'avg_value': avg_value,
        'avg_host': avg_host,

        # ⭐ NEW (bars ke liye)
        'avg_cleanliness_percent': avg_cleanliness_percent,
        'avg_location_percent': avg_location_percent,
        'avg_value_percent': avg_value_percent,
        'avg_host_percent': avg_host_percent,

        'reviews': reviews,
        'total_reviews': total_reviews,
    }

    return render(request, 'rooms/room_details.html', context)
#===============saved rooms ====================

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Listing, Saved_Rooms 


@login_required
def toggle_save_room(request, room_id):
    if request.method == "POST":
        room = get_object_or_404(Listing, id=room_id)
        saved_room, created = Saved_Rooms.objects.get_or_create(user=request.user, room=room)

        if not created:
            saved_room.delete()
            return JsonResponse({   # ✅ if ke andar, sahi jagah
                'status': 'success', 
                'action': 'removed', 
                'room_id': room_id
            })

        # ✅ Yeh tab chalega jab naya save hua ho (created=True)
        return JsonResponse({
            'status': 'success',
            'action': 'saved',
            'room_data': {
                'id': room.id,
                'title': room.title,
                'rent': room.rent,
                'area': room.area,
                'city': room.city,
                'image_url': room.images.first().image.url if room.images.exists() else 'https://via.placeholder.com/400x300',
            }
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

#===============review rooms====================
from .models import Listing, Amenity, ListingImage, Review
from django.contrib import messages

@login_required
def submit_review(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Listing, id=room_id)

        if Review.objects.filter(listing=room, user=request.user).exists():
            messages.error(request, 'already submitted!')
            return redirect('room_details_by_id', room_id=room_id)

        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if rating and comment:
            Review.objects.create(
                listing=room,
                user=request.user,
                rating=int(rating),
                cleanliness_rating=int(request.POST.get('cleanliness_rating') or 3),
                location_rating=int(request.POST.get('location_rating') or 3),
                value_rating=int(request.POST.get('value_rating') or 3),
                host_rating=int(request.POST.get('host_rating') or 3),
                comment=comment,
            )
            messages.success(request, 'Review submit ho gayi! ⭐')

            rating = request.POST.get('rating')
            comment = request.POST.get('comment', '').strip()
            print("DEBUG rating:", rating)
            print("DEBUG comment:", comment)
            print("DEBUG POST data:", request.POST)

        return redirect('room_details_by_id', room_id=room_id)

    return redirect('room_details_by_id', room_id=room_id)



#==========match view============
@login_required(login_url='/login/')
def matches(request):
    return render(request, 'rooms/matches.html')

#=======match details view===========


@login_required
def ai_match_view(request):
    user_prefs = (
        f"Gender: {request.GET.get('gender', 'Any')}, "
        f"Occupation: {request.GET.get('occupation', 'Any')}, "
        f"Sleep schedule: {request.GET.get('sleep', 'Any')}, "
        f"Cleanliness: {request.GET.get('cleanliness', 'Any')}, "
        f"Guest policy: {request.GET.get('guest_policy', 'Any')}, "
        f"City: {request.GET.get('city', 'Any')}, "
        f"Budget: {request.GET.get('budget', 'Any')}"
    )

    rooms = Listing.objects.filter(is_published=True)

    results = []
    for room in rooms:
        response = get_vibe_score(user_prefs, room.get_preference_text())
        data = json.loads(response)
        results.append({
            "room_id": room.id,
            "title": room.title,
            "city": room.city,
            "rent": room.rent,
            "vibe_score": data["score"],
            "reason": data["reason"]
        })

    results.sort(key=lambda x: x["vibe_score"], reverse=True)

    return JsonResponse({"matches": results})