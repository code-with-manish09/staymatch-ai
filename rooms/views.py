from datetime import date
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from httpx import request
from .models import FlatmateProfile, Listing, Amenity, ListingImage, Review, SavedFlatmate
from django.http import JsonResponse  
from rooms.services.services import get_room_faqs, get_vibe_score
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages



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
@login_required
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
@login_required
def match_gateway(request):
    return render(request, 'rooms/match_gateway.html')


@login_required
def room_matches(request):
    return render(request, 'rooms/room_matches.html')

@login_required
def flatmate_match(request):
    return render(request, 'rooms/flatmate_match.html')


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

    city = request.GET.get('city')
    if city:
        rooms = rooms.filter(city__iexact=city)

    budget = request.GET.get('budget')
    if budget:
        try:
            rooms = rooms.filter(rent__lte=int(budget))
        except ValueError:
            pass

    room_type = request.GET.get('room_type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    furnishing = request.GET.get('furnishing')
    if furnishing:
        if 'Fully' in furnishing:
            rooms = rooms.filter(furnishing_status='Fully')
        elif 'Semi' in furnishing:
            rooms = rooms.filter(furnishing_status='Semi')
        elif 'Unfurnished' in furnishing:
            rooms = rooms.filter(furnishing_status='Unfurnished')

    results = []
    for room in rooms:
        try:
            response = get_vibe_score(user_prefs, room.get_preference_text())
            clean = response.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            if not clean:
                continue
            data = json.loads(clean)
            score = data.get("score")
            reason = data.get("reason", "")
            if score is None:
                continue
        except Exception as e:
            print("AI match skip, room", room.id, ":", e)
            continue

        # ✅ Sirf 60+ score wale show karo
        if score >= 60:
            results.append({
                "room_id": room.id,
                "title": room.title,
                "city": room.city,
                "rent": room.rent,
                "vibe_score": score,
                "reason": reason
            })

    results.sort(key=lambda x: x["vibe_score"], reverse=True)
    return JsonResponse({"matches": results})
     
#===============room faqs====================
@login_required
def room_faqs(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Listing, id=room_id)
        question = request.POST.get('question', '').strip()
        
        if not question:
            return JsonResponse({'error': 'Question empty hai'}, status=400)
        
        answer = get_room_faqs(room.get_preference_text(), question)
        return JsonResponse({'answer': answer})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

#===============edit room====================

AMENITIES_DATA = [
    ('📶', 'High-Speed WiFi'),
    ('❄️', 'Air Conditioning'),
    ('🛏️', 'Bed & Mattress'),
    ('🧺', 'Washing Machine'),
    ('🍳', 'Kitchen Access'),
    ('🚿', 'Attached Bath'),
    ('🅿️', 'Parking'),
    ('🏋️', 'Gym Access'),
    ('🔒', '24h Security'),
    ('🛗', 'Lift / Elevator'),
    ('⚡', 'Power Backup'),
    ('🐾', 'Pet Friendly'),
]

AMENITIES_DATA = [
    ('📶', 'High-Speed WiFi'),
    ('❄️', 'Air Conditioning'),
    ('🛏️', 'Bed & Mattress'),
    ('🧺', 'Washing Machine'),
    ('🍳', 'Kitchen Access'),
    ('🚿', 'Attached Bath'),
    ('🅿️', 'Parking'),
    ('🏋️', 'Gym Access'),
    ('🔒', '24h Security'),
    ('🛗', 'Lift / Elevator'),
    ('⚡', 'Power Backup'),
    ('🐾', 'Pet Friendly'),
]
 
 
@login_required
def edit_room(request, pk):
    room = get_object_or_404(Listing, pk=pk, owner=request.user)
 
    if request.method == 'POST':
 
        # Step 1: Basics — .strip() se empty string bhi save hogi
        room.title = request.POST.get('title', '').strip()
        room.city = request.POST.get('city', '').strip()
        room.area = request.POST.get('area', '').strip()
        room.address = request.POST.get('address', '').strip()
        room.room_type = request.POST.get('room_type', '').strip()
        room.bhk_config = request.POST.get('bhk_config', '1 BHK').strip()
        room.floor = request.POST.get('floor', '').strip()
        room.available_from = request.POST.get('available_from')
        room.min_stay = request.POST.get('min_stay', 'Flexible')
 
        # Step 2: Pricing
        room.rent = to_int(request.POST.get('rent'), 12000)
        room.deposit = request.POST.get('deposit', 'Negotiable')
        room.maintenance = request.POST.get('maintenance', 'Included in rent')
 
        # Included items
        included = request.POST.get('included_items', '')
        room.included_wifi = 'WiFi' in included
        room.included_electricity = 'Electricity' in included
        room.included_water = 'Water' in included
        room.included_gas = 'Gas' in included
        room.included_cooking = 'Cooking' in included
        room.included_housekeeping = 'Housekeeping' in included
 
        # Step 3: Furnishing
        furnishing = request.POST.get('furnishing_status', 'Unfurnished')
        if 'Fully' in furnishing:
            room.furnishing_status = 'Fully'
        elif 'Semi' in furnishing:
            room.furnishing_status = 'Semi'
        else:
            room.furnishing_status = 'Unfurnished'
 
        # Step 5: Description
        room.description = request.POST.get('description', '').strip()
        room.house_rules = request.POST.get('house_rules', '').strip()
        room.nearest_metro = request.POST.get('nearest_metro', '').strip()
        room.distance_to_hub = request.POST.get('distance_to_hub', '').strip()
 
        # Step 6: Preferences
        room.pref_gender = request.POST.get('pref_gender', 'Any')
        room.pref_occupation = request.POST.get('pref_occupation', 'Any')
        room.sleep_schedule = request.POST.get('sleep_schedule', 'No preference').strip()
        room.cleanliness_level = to_int(request.POST.get('cleanliness_level'), 7)
        room.guest_policy = request.POST.get('guest_policy', 'Occasional guests OK').strip()
 
        # Step 7: Contact
        room.contact_name = request.POST.get('contact_name', '').strip()
        room.contact_phone = request.POST.get('contact_phone', '').strip()
        room.contact_email = request.POST.get('contact_email', '').strip()
 
        room.save()
 
        # Amenities — get_or_create se naye bhi ban jayenge
        amenities_str = request.POST.get('amenities', '')
        room.amenities.clear()
        if amenities_str:
            for name in [a.strip() for a in amenities_str.split(',') if a.strip()]:
                amenity, _ = Amenity.objects.get_or_create(
                    name=name,
                    defaults={'icon': '✨'}
                )
                room.amenities.add(amenity)
 
        # Delete marked photos
        for img_id in request.POST.getlist('delete_images'):
            if img_id:
                ListingImage.objects.filter(id=img_id, listing=room).delete()
 
        # New photos
        for img in request.FILES.getlist('new_images'):
            ListingImage.objects.create(listing=room, image=img)
 
        messages.success(request, '✅ Room updated successfully!')
        return redirect('room_details_by_id', room_id=room.pk)
 
    # GET request
    amenity_names = list(room.amenities.values_list('name', flat=True))
 
    included_items = []
    if room.included_wifi: included_items.append('WiFi')
    if room.included_electricity: included_items.append('Electricity')
    if room.included_water: included_items.append('Water')
    if room.included_gas: included_items.append('Gas')
    if room.included_cooking: included_items.append('Cooking')
    if room.included_housekeeping: included_items.append('Housekeeping')
 
    return render(request, 'rooms/edit_room.html', {
        'room': room,
        'amenity_names': amenity_names,
        'amenities_data': AMENITIES_DATA,
        'included_items': included_items,
    })
 
 
#===============delete room====================
 
@login_required
def delete_room(request, pk):
    room = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        room.delete()
        messages.success(request, '✅ Room deleted successfully!')
        return redirect('dashboard')
    return redirect('room_details_by_id', room_id=pk)

#===============post gate====================
@login_required
def post_gate(request):
    return render(request, 'rooms/post_gate.html')


#==============post flatmate====================

def to_int(val, default=0):
    try:
        return int(val)
    except:
        return default


def post_flatmate(request):
    from .models import FlatmateProfile

    if request.method == 'POST':
        
        try:
            tags_str = request.POST.get('interest_tags', '')
            tags_json = json.dumps([t.strip() for t in tags_str.split(',') if t.strip()])

            FlatmateProfile.objects.create(
                user            = request.user,
                name            = request.POST.get('name', ''),
                age             = to_int(request.POST.get('age'), 22),
                gender          = request.POST.get('gender', ''),
                occupation      = request.POST.get('occupation', ''),
                city            = request.POST.get('city', ''),
                preferred_area  = request.POST.get('preferred_area', ''),
                language_pref   = request.POST.get('language_pref', ''),
                bio             = request.POST.get('bio', ''),
                profile_photo   = request.FILES.get('profile_photo'),
                max_budget      = to_int(request.POST.get('max_budget'), 12000),
                room_type_pref  = request.POST.get('room_type_pref', 'Any'),
                move_in         = request.POST.get('move_in', 'Flexible'),
                stay_duration   = request.POST.get('stay_duration', 'Flexible'),
                interest_tags   =   tags_json,  
                sleep_schedule  = request.POST.get('sleep_schedule', 'No Preference'),
                cleanliness_level = to_int(request.POST.get('cleanliness_level'), 7),
                noise_tolerance = request.POST.get('noise_tolerance', 'Moderate OK'),
                guest_policy    = request.POST.get('guest_policy', 'Occasional OK'),
                work_style      = request.POST.get('work_style', 'Hybrid'),
                smoking         = request.POST.get('smoking', 'Non-smoker'),
                alcohol         = request.POST.get('alcohol', "Don't drink"),
                pets            = request.POST.get('pets', 'No pets'),
                pref_gender     = request.POST.get('pref_gender', 'Any'),
                pref_age_range  = request.POST.get('pref_age_range', 'Any'),
                pref_occupation = request.POST.get('pref_occupation', 'Any'),
                flatmate_expectation = request.POST.get('flatmate_expectation', ''),
                contact_phone   = request.POST.get('contact_phone', ''),
                contact_email   = request.POST.get('contact_email', ''),
                contact_preference = request.POST.get('contact_preference', 'WhatsApp'),
                contact_visibility = request.POST.get('contact_visibility', 'Show after connect only'),
                vibe_score      = to_int(request.POST.get('vibe_score'), 0),
            )
            print("Save ho gaya")
            messages.success(request, 'Profile post ho gayi! 🎉')
            return redirect('dashboard')

        except Exception as e:
            print("ERROR:", e)

            messages.error(request, f'Kuch galat hua: {str(e)}')
            return redirect('post_flatmate')

    return render(request, 'rooms/post_flatmate.html')

#===============edit flatmate====================
@login_required
def edit_flatmate(request, pk):
    from .models import FlatmateProfile
    post = get_object_or_404(FlatmateProfile, pk=pk, user=request.user)
    
    if request.method == 'POST':
        try:
            tags_str = request.POST.get('interest_tags', '')
            tags_json = json.dumps([t.strip() for t in tags_str.split(',') if t.strip()])
            
            post.name = request.POST.get('name', '')
            post.age = to_int(request.POST.get('age'), 22)
            post.gender = request.POST.get('gender', '')
            post.occupation = request.POST.get('occupation', '')
            post.city = request.POST.get('city', '')
            post.preferred_area = request.POST.get('preferred_area', '')
            post.language_pref = request.POST.get('language_pref', '')
            post.bio = request.POST.get('bio', '')
            if request.FILES.get('profile_photo'):
                post.profile_photo = request.FILES.get('profile_photo')
            post.max_budget = to_int(request.POST.get('max_budget'), 12000)
            post.room_type_pref = request.POST.get('room_type_pref', 'Any')
            post.move_in = request.POST.get('move_in', 'Flexible')
            post.stay_duration = request.POST.get('stay_duration', 'Flexible')
            post.interest_tags = tags_json
            post.sleep_schedule = request.POST.get('sleep_schedule', 'No Preference')
            post.cleanliness_level = to_int(request.POST.get('cleanliness_level'), 7)
            post.noise_tolerance = request.POST.get('noise_tolerance', 'Moderate OK')
            post.guest_policy = request.POST.get('guest_policy', 'Occasional OK')
            post.work_style = request.POST.get('work_style', 'Hybrid')
            post.smoking = request.POST.get('smoking', 'Non-smoker')
            post.alcohol = request.POST.get('alcohol', "Don't drink")
            post.pets = request.POST.get('pets', 'No pets')
            post.pref_gender = request.POST.get('pref_gender', 'Any')
            post.pref_age_range = request.POST.get('pref_age_range', 'Any')
            post.pref_occupation = request.POST.get('pref_occupation', 'Any')
            post.flatmate_expectation = request.POST.get('flatmate_expectation', '')
            post.contact_phone = request.POST.get('contact_phone', '')
            post.contact_email = request.POST.get('contact_email', '')
            post.contact_preference = request.POST.get('contact_preference', 'WhatsApp')
            post.contact_visibility = request.POST.get('contact_visibility', 'Show after connect only')
            post.vibe_score = to_int(request.POST.get('vibe_score'), 0)
            post.save()
            messages.success(request, 'Profile update ho gayi! 🎉')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Kuch galat hua: {str(e)}')
    
    return render(request, 'rooms/edit_flatmate.html', {'post': post})

#===============flatmate details====================
from django.shortcuts import render, get_object_or_404
from .models import FlatmateProfile

from inbox.models import FlatmateInquiry
@login_required
def flatmate_detail(request, pk):
    profile = get_object_or_404(FlatmateProfile, id=pk)
    
    user_already_inquired = False
    if request.user.is_authenticated:
        user_already_inquired = FlatmateInquiry.objects.filter(
            sender=request.user,
            flatmate_profile=profile
        ).exists()

    return render(request, 'rooms/flatmate_details.html', {
        'post': profile,
        'user_already_inquired': user_already_inquired,
    })
#===============delete flatmate====================
# views.py
@login_required
def delete_flatmate(request, pk):
    from .models import FlatmateProfile
    post = get_object_or_404(FlatmateProfile, pk=pk, user=request.user)
    post.delete()
    messages.success(request, 'Flatmate post delete ho gayi! 🗑️')
    return redirect('dashboard')

#===============saved flatmates====================


@login_required
def toggle_save_flatmate(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(FlatmateProfile, id=profile_id)
        saved, created = SavedFlatmate.objects.get_or_create(user=request.user, profile=profile)
        if not created:
            saved.delete()
            return JsonResponse({'status': 'success', 'action': 'removed'})
        return JsonResponse({'status': 'success', 'action': 'saved'})
    return JsonResponse({'status': 'error'}, status=400)

#===============flatmate match====================
@login_required
def ai_flatmate_match_view(request):
    user_prefs = (
        f"Gender: {request.GET.get('gender', 'Any')}, "
        f"Occupation: {request.GET.get('occupation', 'Any')}, "
        f"City: {request.GET.get('city', 'Any')}, "
        f"Budget: {request.GET.get('budget', 'Any')}, "
        f"Room type needed: {request.GET.get('room_type', 'Any')}, "
        f"Move-in: {request.GET.get('move_in', 'Any')}, "
        f"Sleep schedule: {request.GET.get('sleep', 'Any')}, "
        f"Cleanliness: {request.GET.get('cleanliness', 'Any')}, "
        f"Guest policy: {request.GET.get('guest_policy', 'Any')}, "
        f"Work style: {request.GET.get('work_style', 'Any')}, "
        f"Noise tolerance: {request.GET.get('noise', 'Any')}, "
        f"Smoking: {request.GET.get('smoking', 'Any')}, "
        f"Alcohol: {request.GET.get('alcohol', 'Any')}, "
        f"Pets: {request.GET.get('pets', 'Any')}, "
        f"Language: {request.GET.get('language', 'Any')}, "
        f"Preferred flatmate gender: {request.GET.get('pref_gender', 'Any')}, "
        f"Preferred flatmate occupation: {request.GET.get('pref_occupation', 'Any')}, "
        f"Preferred age range: {request.GET.get('pref_age', 'Any')}"
    )

    profiles = FlatmateProfile.objects.filter(is_active=True)

    city = request.GET.get('city')
    if city:
        profiles = profiles.filter(city__iexact=city)

    results = []
    for profile in profiles:
        try:
            profile_text = profile.get_preference_text()
            response = get_vibe_score(user_prefs, profile_text)
            clean = response.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            if not clean:
                continue
            data = json.loads(clean)
            score = data.get("score")
            reason = data.get("reason", "")
            if score is None:
                continue
        except Exception as e:
            print("AI flatmate match skip, profile", profile.id, ":", e)
            continue
        print("SCORE:", profile.name, "→", score)   # flatmate view mein

        if score >= 50:
            results.append({
                "profile_id": profile.id,
                "name": profile.name,
                "age": profile.age,
                "occupation": profile.occupation,
                "city": profile.city,
                "budget": profile.max_budget,
                "room_type": profile.room_type_pref,
                "sleep": profile.sleep_schedule,
                "vibe_score": score,
                "reason": reason,
            })

    results.sort(key=lambda x: x["vibe_score"], reverse=True)
    return JsonResponse({"matches": results})