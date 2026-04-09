from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Listing, Amenity, ListingImage

@login_required 
def post_room(request):
    # Sirf logged-in users hi room list kar sakein
    if request.method == 'POST':
        # 1. Basic Data uthana (HTML 'name' attribute ke hisaab se)
        title = request.POST.get('title')
        city = request.POST.get('city')
        area = request.POST.get('area')
        room_type = request.POST.get('room_type')
        rent = request.POST.get('rent')
        available_from = request.POST.get('available_from')
        description = request.POST.get('description')
        
        # 2. Listing Object Create karna
        new_listing = Listing.objects.create(
            owner=request.user,
            title=title,
            city=city,
            area=area,
            room_type=room_type,
            rent=rent,
            available_from=available_from,
            description=description,
            # Baaki fields bhi aise hi add karein...
        )

        # 3. Amenities Handle karna (ManyToMany Field)
        # Form mein agar multi-select hai ya multiple checkboxes hain:
        selected_amenities = request.POST.getlist('amenities') # ['WiFi', 'AC']
        for ame_name in selected_amenities:
            amenity_obj, created = Amenity.objects.get_or_create(name=ame_name)
            new_listing.amenities.add(amenity_obj)

        # 4. Multiple Images Handle karna
        images = request.FILES.getlist('images') # HTML mein <input type="file" name="images" multiple>
        for img in images:
            ListingImage.objects.create(listing=new_listing, image=img)

        return redirect('success_page') # Save hone ke baad redirect

    return render(request, 'rooms/post_room.html')

def room_details(request):

    return render (request, 'rooms/room_details.html')    



