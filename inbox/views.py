from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from .models import Message
from rooms.models import Listing

# ─── helper: sidebar conversations ───────────────────────────────────────────
def get_conversations(user):
    all_msgs = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    )

    seen = []        # (listing_id, other_user_id) dono track karo
    conversations = []

    for msg in all_msgs.order_by('-created_at'):
        # Other user kaun hai
        if msg.sender == user:
            other = msg.recipient
        else:
            other = msg.sender

        key = (msg.listing_id, other.id)   # ✅ listing + user dono ka pair

        if key not in seen:
            seen.append(key)

            unread = Message.objects.filter(
                recipient=user,
                listing=msg.listing,
                sender=other,
                is_read=False
            ).count()

            conversations.append({
                'listing': msg.listing,
                'last_msg': msg,
                'other_user': other,
                'unread': unread,
            })

    return conversations
# ─── inbox view (sirf sidebar dikhao, koi chat select nahi) ──────────────────
@login_required
def inbox(request):
    conversations = get_conversations(request.user)

    return render(request, 'inbox/inbox.html', {
        'conversations': conversations,
        'messages': [],          # koi chat open nahi
        'active_listing': None,
    })


# ─── chat view (ek listing ki sari messages dikhao) ──────────────────────────
@login_required
def chat_view(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    # Doosra banda kaun hai determine karo
    if request.user == listing.owner:
        # Owner hai toh URL se other_user_id lena hoga
        other_user_id = request.GET.get('user')
        if not other_user_id:
            # Koi user select nahi — pehli conversation pe bhejo
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
        # Normal user hai — other_user hamesha owner hoga
        other_user = listing.owner

    # Sirf inhi do logon ke beech ki messages
    messages = Message.objects.filter(
        listing=listing
    ).filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')

    # Read mark karo
    messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    conversations = get_conversations(request.user)

    return render(request, 'inbox/inbox.html', {
        'conversations': conversations,
        'messages': messages,
        'active_listing': listing,
        'other_user': other_user,
    })

from django.urls import reverse

@login_required
def send_message(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=listing_id)
        body = request.POST.get('body', '').strip()

        if body:
            if request.user == listing.owner:
                other_user_id = request.POST.get('other_user_id')
                if not other_user_id:
                    first_msg = Message.objects.filter(
                        listing=listing
                    ).exclude(sender=listing.owner).first()
                    if not first_msg:
                        return redirect('inbox')
                    recipient = first_msg.sender
                    other_user_id = recipient.id
                else:
                    from django.contrib.auth.models import User
                    recipient = get_object_or_404(User, id=int(other_user_id))

                Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    listing=listing,
                    body=body,
                )
                # ✅ reverse use karo — hardcoded URL nahi
                return redirect(
                    reverse('chat_view', args=[listing_id]) + f'?user={other_user_id}'
                )
            else:
              Message.objects.create(
              sender=request.user,
              recipient=listing.owner,
              listing=listing,
              body=body,
        )
        return redirect(
              reverse('chat_view', args=[listing_id])
 )

    return redirect('inbox')

#=========== unread count API for AJAX polling ==============

from django.http import JsonResponse

@login_required
def unread_count_api(request):
    conversations = get_conversations(request.user)
    unread = sum(1 for conv in conversations if conv['unread'] > 0)
    unread_data = [
        {
            'username': conv['other_user'].username,
            'message': conv['last_msg'].body,
            'listing': conv['listing'].title,
            'count': conv['unread'],
            'last_msg_id': conv['last_msg'].id  

        }
        for conv in conversations if conv['unread'] > 0
    ]
    return JsonResponse({'unread_count': unread, 'conversations': unread_data})