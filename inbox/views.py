import profile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from httpx import request
from .models import Message
from rooms.models import Listing, FlatmateProfile


# ─── helper: sidebar conversations ───────────────────────────────────────────
def get_conversations(user):
    all_msgs = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).select_related('listing', 'flatmate_profile', 'sender', 'recipient')

    seen = []
    conversations = []

    for msg in all_msgs.order_by('-created_at'):
        other = msg.recipient if msg.sender == user else msg.sender

        if msg.listing_id:
            key = ('room', msg.listing_id, other.id)
        elif msg.flatmate_profile_id:
            key = ('flatmate',  other.id)
        else:
            continue

        if key not in seen:
            seen.append(key)

            if msg.listing_id:
                unread = Message.objects.filter(
                    recipient=user, sender=other,
                    listing=msg.listing, is_read=False
                ).count()
            else:
                unread = Message.objects.filter(
                    recipient=user, sender=other,
                  flatmate_profile__isnull=False, is_read=False
                ).count()

            conversations.append({
                'listing'          : msg.listing,
                'flatmate_profile' : msg.flatmate_profile,
                'last_msg'         : msg,
                'other_user'       : other,
                'unread'           : unread,
                'type'             : 'room' if msg.listing_id else 'flatmate',
            })

    return conversations


# ─── inbox view ───────────────────────────────────────────────────────────────
@login_required
def inbox(request):
    conversations = get_conversations(request.user)
    return render(request, 'inbox/inbox.html', {
        'conversations'  : conversations,
        'chat_messages'  : [],
        'active_listing' : None,
    })


# ─── room chat view ───────────────────────────────────────────────────────────
@login_required
def chat_view(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.user == listing.owner:
        other_user_id = request.GET.get('user')
        if not other_user_id:
            first_msg = Message.objects.filter(
                listing=listing,
                recipient=listing.owner
            ).first()
            if first_msg:
                return redirect(f"{request.path}?user={first_msg.sender.id}")
            else:
                return redirect('inbox')
        from django.contrib.auth.models import User
        other_user = get_object_or_404(User, id=other_user_id)
    else:
        other_user = listing.owner

    messages = Message.objects.filter(
        listing=listing
    ).filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user,   recipient=request.user)
    ).order_by('created_at')

    messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    conversations = get_conversations(request.user)

    return render(request, 'inbox/inbox.html', {
        'conversations'  : conversations,
        'chat_messages'  : messages,
        'active_listing' : listing,
        'other_user'     : other_user,
    })


# ─── room message send ────────────────────────────────────────────────────────
@login_required
def send_message(request, listing_id):
    if request.method != 'POST':
        return redirect('inbox')

    listing = get_object_or_404(Listing, id=listing_id)
    body    = request.POST.get('body', '').strip()

    if not body:
        return redirect('inbox')

    if request.user == listing.owner:
        other_user_id = request.POST.get('other_user_id')
        if not other_user_id:
            first_msg = Message.objects.filter(
                listing=listing
            ).exclude(sender=listing.owner).first()
            if not first_msg:
                return redirect('inbox')
            recipient     = first_msg.sender
            other_user_id = recipient.id
        else:
            from django.contrib.auth.models import User
            recipient = get_object_or_404(User, id=int(other_user_id))

        Message.objects.create(
            sender=request.user, recipient=recipient,
            listing=listing, body=body,
        )
        return redirect(
            reverse('chat_view', args=[listing_id]) + f'?user={other_user_id}'
        )
    else:
        # ✅ Sirf pehli baar inquiry_count badhao
        already_messaged = Message.objects.filter(
            sender=request.user,
            listing=listing
        ).exists()

        if not already_messaged:
            from django.db.models import F
            Listing.objects.filter(id=listing_id).update(
                inquiry_count=F('inquiry_count') + 1
            )

        Message.objects.create(
            sender=request.user, recipient=listing.owner,
            listing=listing, body=body,
        )
        return redirect(reverse('chat_view', args=[listing_id]))


# ─── flatmate:  (auto first message) ────────────────────────────
@login_required
def send_flatmate_message(request, profile_id):
    if request.method != 'POST':
        return redirect('inbox')

    profile = get_object_or_404(FlatmateProfile, id=profile_id)

    if profile.user == request.user:
        return redirect('flatmate_detail', pk=profile_id)

    body = request.POST.get('body', '').strip()

    # Agar body nahi hai (pehli baar CTA button se aaya)
    # toh auto-message bhejo sirf ek baar
    if not body:
        already_exists = Message.objects.filter(
            sender=request.user,
            recipient=profile.user,
            flatmate_profile=profile
        ).exists()

        if not already_exists:
            Message.objects.create(
                sender           = request.user,
                recipient        = profile.user,
                flatmate_profile = profile,
                listing          = None,
                body             = "Hi, I am interested in connecting with you as a flatmate!",
            )
    else:
        # Normal typed message
        Message.objects.create(
            sender           = request.user,
            recipient        = profile.user,
            flatmate_profile = profile,
            listing          = None,
            body             = body,
        )

    return redirect(
        reverse('flatmate_chat', args=[profile_id]) + f'?user={profile.user.id}'
    )
# ─── flatmate chat view ───────────────────────────────────────────────────────
from django.contrib.auth.models import User
@login_required
def flatmate_chat_view(request, profile_id):
    profile = get_object_or_404(FlatmateProfile, id=profile_id)

    other_user_id = request.GET.get('user') or request.POST.get('other_user_id')

    if other_user_id:
        other_user = get_object_or_404(User, id=other_user_id)
    elif request.user == profile.user:
        return redirect('inbox')
    else:
        other_user = profile.user

    # Dono ke beech messages
    chat_messages = Message.objects.filter(
        flatmate_profile__isnull=False
    ).filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user,   recipient=request.user)
    ).order_by('created_at')
    # Read mark 
    chat_messages.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)

   # POST — naya message
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(
                sender           = request.user,
                recipient        = other_user,
                flatmate_profile = profile,
                listing          = None,
                body             = body,
            )
        return redirect(reverse('flatmate_chat', args=[profile_id]) + f'?user={other_user.id}')

    conversations = get_conversations(request.user)

    return render(request, 'inbox/inbox.html', {
        'conversations'          : conversations,
        'chat_messages'          : chat_messages,
        'active_listing'         : None,
        'active_flatmate_profile': profile,
        'other_user'             : other_user,
    })


# ─── unread count API ─────────────────────────────────────────────────────────
@login_required
def unread_count_api(request):
    conversations = get_conversations(request.user)

    unread_data = []
    for conv in conversations:
        if conv['unread'] > 0:
            entry = {
                'username'    : conv['other_user'].username,
                'message'     : conv['last_msg'].body,
                'count'       : conv['unread'],
                'last_msg_id' : conv['last_msg'].id,
                'type'        : conv['type'],
            }
            if conv['type'] == 'room':
                entry['listing'] = conv['listing'].title
            else:
                entry['profile'] = conv['flatmate_profile'].name
            unread_data.append(entry)

    total_unread = sum(c['unread'] for c in conversations if c['unread'] > 0)

    return JsonResponse({
        'unread_count'  : total_unread,
        'conversations' : unread_data,
    })