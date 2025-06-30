from django.db.models import Q
from .models import Room, MessageRequest, DirectMessageRoom, DirectMessage
from django.contrib.auth.models import User

def public_rooms(request):
    rooms = Room.objects.all()
    return {'rooms': rooms}


def message_notifications(request):
    if request.user.is_authenticated:
        incoming_requests = MessageRequest.objects.filter(to_user=request.user, is_accepted=False)
        accepted_requests = MessageRequest.objects.filter(from_user=request.user, is_accepted=True)
        return {
            'incoming_requests': incoming_requests,
            'accepted_requests': accepted_requests,
        }
    return {}

def private_chat_users(request):
    if not request.user.is_authenticated:
        return {}

    accepted_requests = MessageRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        is_accepted=True
    )

    private_chat_users = []
    for req in accepted_requests:
        other_user = req.to_user if req.from_user == request.user else req.from_user

        # Find DM Room
        room = DirectMessageRoom.objects.filter(
            Q(user1=request.user, user2=other_user) |
            Q(user1=other_user, user2=request.user)
        ).first()

        # Check if the other_user has unread messages sent to request.user
        has_unread = False
        if room:
            has_unread = DirectMessage.objects.filter(
                room=room,
                sender=other_user,
                is_read=False
            ).exists()

        # Attach indicator dynamically
        other_user.has_unread = has_unread
        private_chat_users.append(other_user)

    return {'private_chat_users': private_chat_users}
