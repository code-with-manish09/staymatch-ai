from django.shortcuts import render

def post_room(request):
    return render(request, 'rooms/post_room.html')

def room_details(request):

    return render (request, 'rooms/room_details.html')    