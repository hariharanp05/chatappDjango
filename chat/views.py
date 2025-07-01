from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse


from .forms import RoomForm, MessageForm
from .models import (
    Message,
    MessageRequest,
    DirectMessageRoom,
    DirectMessage,
    BlockedUser,
)

# PUBLIC CHAT

@login_required
def chat_home(request):
    form = RoomForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        room_name = form.cleaned_data['room_name']
        messages.success(request, f"Joined public room: {room_name}")
        return redirect('chat_room', room_name=room_name)

    accepted_requests = MessageRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        is_accepted=True
    )

    private_chat_users = []
    for req in accepted_requests:
        other_user = req.to_user if req.from_user == request.user else req.from_user

        # Find the DM room
        room = DirectMessageRoom.objects.filter(
            Q(user1=request.user, user2=other_user) |
            Q(user1=other_user, user2=request.user)
        ).first()

        # Check for unread messages from the other user
        has_unread = False
        if room:
            has_unread = DirectMessage.objects.filter(
                room=room,
                sender=other_user,
                is_read=False
            ).exists()

        other_user.has_unread = has_unread
        private_chat_users.append(other_user)

    # ✅ Add this line for the popup modal
    blocked_users = BlockedUser.objects.filter(blocker=request.user).select_related('blocked')

    return render(request, 'chat/index.html', {
        'form': form,
        'private_chat_users': private_chat_users,
        'blocked_users': [entry.blocked for entry in blocked_users],  # Just list of User objects
    })


@login_required
def chat_room(request, room_name):
    db_messages = Message.objects.filter(room=room_name).order_by('date_added')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            Message.objects.create(
                username=request.user.username,
                room=room_name,
                message_content=form.cleaned_data.get('content'),
                file=form.cleaned_data.get('file'),
                profile_pic=request.user.profile.profile_picture.url if hasattr(request.user, 'profile') else ''
            )
            return redirect('chat_room', room_name=room_name)
    else:
        form = MessageForm()

    return render(request, 'chat/chatroom.html', {
        'room_name': room_name,
        'title': room_name,
        'db_messages': db_messages,
        'form': form,
    })

# MESSAGE REQUESTS

@login_required
def send_message_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if to_user == request.user:
        messages.error(request, "You cannot message yourself.")
    elif MessageRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        messages.info(request, "Message request already sent.")
    else:
        MessageRequest.objects.create(from_user=request.user, to_user=to_user)
        messages.success(request, "Message request sent.")

    return redirect('user_profile', username=to_user.username)

@login_required
def accept_message_request(request, request_id):
    msg_request = get_object_or_404(MessageRequest, id=request_id, to_user=request.user)
    msg_request.is_accepted = True
    msg_request.save()

    user1 = min(request.user, msg_request.from_user, key=lambda u: u.id)
    user2 = max(request.user, msg_request.from_user, key=lambda u: u.id)

    DirectMessageRoom.objects.get_or_create(user1=user1, user2=user2)

    messages.success(request, "Message request accepted.")
    return redirect('chat-home')

# BLOCK / UNBLOCK USERS

@login_required
def block_user(request, user_id):
    blocked_user = get_object_or_404(User, id=user_id)
    if blocked_user != request.user:
        BlockedUser.objects.get_or_create(blocker=request.user, blocked=blocked_user)
        messages.success(request, f"Blocked {blocked_user.username}")
    return redirect('chat-home')

@login_required
def unblock_user(request, user_id):
    blocked_user = get_object_or_404(User, id=user_id)
    BlockedUser.objects.filter(blocker=request.user, blocked=blocked_user).delete()
    messages.success(request, f"Unblocked {blocked_user.username}")
    return redirect('chat-home')

# DIRECT MESSAGES

# @login_required
# def direct_messages(request):
#     rooms = DirectMessageRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user))
#     contacts = [room.user2 if room.user1 == request.user else room.user1 for room in rooms]
#     return render(request, 'chat/direct_messages.html', {'contacts': contacts})

@login_required
def private_chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    if BlockedUser.objects.filter(blocker=other_user, blocked=request.user).exists():
        messages.error(request, "You are blocked by this user.")
        return redirect('chat-home')

    accepted = MessageRequest.objects.filter(
        Q(from_user=request.user, to_user=other_user) |
        Q(from_user=other_user, to_user=request.user),
        is_accepted=True
    ).exists()

    if not accepted:
        messages.error(request, "No accepted message request exists.")
        return redirect('user_profile', username=other_user.username)

    room_name = f"dm_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"

    room = DirectMessageRoom.objects.filter(
        Q(user1=request.user, user2=other_user) |
        Q(user1=other_user, user2=request.user)
    ).first()

    if not room:
        messages.error(request, "No DM room exists. Please send a message request first.")
        return redirect('user_profile', username=other_user.username)

    messages_qs = DirectMessage.objects.filter(room=room).order_by('timestamp')

    messages_qs.filter(sender=other_user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            DirectMessage.objects.create(
                room=room,
                sender=request.user,
                message_content=form.cleaned_data.get('content'),
                file=form.cleaned_data.get('file')
            )
            return redirect('private_chat_room', user_id=other_user.id)
    else:
        form = MessageForm()

    return render(request, 'chat/private_chatroom.html', {
        'room_name': room_name,
        'other_user': other_user,
        'db_messages': messages_qs,
        'form': form
    })

# USER PROFILE

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    request_sent = MessageRequest.objects.filter(from_user=request.user, to_user=profile_user).exists()
    request_received = MessageRequest.objects.filter(from_user=profile_user, to_user=request.user, is_accepted=False).first()

    dm_room_exists = DirectMessageRoom.objects.filter(
        Q(user1=request.user, user2=profile_user) |
        Q(user1=profile_user, user2=request.user)
    ).exists()

    is_blocked = BlockedUser.objects.filter(blocker=request.user, blocked=profile_user).exists()
    blocked_by = BlockedUser.objects.filter(blocker=profile_user, blocked=request.user).exists()

    return render(request, 'chat/user_profile.html', {
        'profile_user': profile_user,
        'request_sent': request_sent,
        'request_received': request_received,
        'dm_room_exists': dm_room_exists,
        'is_blocked': is_blocked,
        'blocked_by': blocked_by,
    })

# NOTIFICATIONS

@login_required
def notifications(request):
    pending_requests = MessageRequest.objects.filter(to_user=request.user, is_accepted=False)
    return render(request, 'chat/notifications.html', {'pending_requests': pending_requests})

# BLOCKED USERS LIST

# @login_required
# def blocked_users(request):
#     blocked = BlockedUser.objects.filter(blocker=request.user)
#     return render(request, 'chat/index.html', {'blocked_users': blocked})


@login_required
def ajax_user_search(request):
    query = request.GET.get("q", "")
    users = User.objects.filter(username__icontains=query)[:10]
    data = {"results": [{"username": user.username} for user in users]}
    return JsonResponse(data)
