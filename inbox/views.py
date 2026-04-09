from django.shortcuts import render

def inbox(request):
    return render(request, 'inbox/inbox.html')