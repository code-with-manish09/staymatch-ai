from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from urllib3 import request
from .models import Listing, Amenity, ListingImage

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

def room_details(request, room_id=None):
    # If room_id provided, open that room; otherwise latest room
    qs = Listing.objects.prefetch_related('amenities', 'images')
    if room_id:
        room = qs.filter(id=room_id).first()
    else:
        room = qs.order_by('-created_at').first()
    included = {
        'wifi': room.included_wifi if room else False,
        'electricity': room.included_electricity if room else False,
        'water': room.included_water if room else False,
        'gas': room.included_gas if room else False,
        'cooking': room.included_cooking if room else False,
        'housekeeping': room.included_housekeeping if room else False,
    }

    return render(request, 'rooms/room_details.html', {'room': room, 'included': included})


#===============saved rooms ====================

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Listing, Saved_Rooms # Check spelling here


@login_required
def toggle_save_room(request, room_id):
    if request.method == "POST":
        room = get_object_or_404(Listing, id=room_id)
        saved_room, created = Saved_Rooms.objects.get_or_create(user=request.user, room=room)

        if not created:
            saved_room.delete()
            # Yahan room_id bhej rahe hain taaki JS pehchan sake kaunsa card delete karna hai
            return JsonResponse({'status': 'success', 'action': 'removed', 'room_id': room_id})
        
        # Room ka poora matter JSON mein pack karo
        return JsonResponse({
            'status': 'success', 
            'action': 'saved',
            'room_data': {
                'id': room.id,
                'title': room.title,
                'rent': room.rent,
                'area': room.area,
                'city': room.city,
                # Image check logic
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