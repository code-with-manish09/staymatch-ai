from django.shortcuts import render
from rooms.models import FlatmateProfile

def home(request):
    featured_flatmates = FlatmateProfile.objects.filter(
        is_active=True
    ).order_by('-created_at')[:3]
    
    return render(request, 'home/index.html', {
        'featured_flatmates': featured_flatmates,
    })