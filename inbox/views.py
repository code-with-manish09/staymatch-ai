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

    seen_listings = []
    conversations = []

    for msg in all_msgs.order_by('-created_at'):
        if msg.listing_id not in seen_listings:
            seen_listings.append(msg.listing_id)

            unread = Message.objects.filter(
                recipient=user,
                listing=msg.listing,
                is_read=False
            ).count()

            # ✅ Yeh fix hai — recipient == user toh other = sender, warna other = recipient
            if msg.sender == user:
                other = msg.recipient
            else:
                other = msg.sender

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

    # Sirf is listing ki messages jo mere saath hain
    messages = Message.objects.filter(
        listing=listing
    ).filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('created_at')

    # Jo messages mujhe mile hain unhe read mark karo
    messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    # Sidebar ke liye conversations
    conversations = get_conversations(request.user)

    # Doosra banda kaun hai?
    first_msg = messages.first()
    if first_msg:
        other_user = first_msg.sender if first_msg.recipient == request.user else first_msg.recipient
    else:
        other_user = listing.owner  # agar koi message nahi abhi tak

    return render(request, 'inbox/inbox.html', {
        'conversations': conversations,
        'messages': messages,
        'active_listing': listing,
        'other_user': other_user,
    })


# ─── send message ─────────────────────────────────────────────────────────────
@login_required
def send_message(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=listing_id)
        body = request.POST.get('body', '').strip()

        if body:
            # ✅ Agar main owner hoon toh recipient = pehle wala sender
            # Agar main owner nahi hoon toh recipient = owner
            if request.user == listing.owner:
                # Owner reply kar raha hai — pehla message dhundo kis ne bheja tha
                first_msg = Message.objects.filter(
                    listing=listing
                ).exclude(sender=listing.owner).first()

                if first_msg:
                    recipient = first_msg.sender
                else:
                    return redirect('chat_view', listing_id=listing_id)
            else:
                # Normal user message kar raha hai owner ko
                recipient = listing.owner

            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                listing=listing,
                body=body,
            )

    return redirect('chat_view', listing_id=listing_id)