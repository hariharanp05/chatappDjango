"""
Context processor for adding public rooms to base template
"""
from .models import Room, MessageRequest, DirectMessageRoom
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

# chat/context_processors.py


def message_rooms(request):
    if request.user.is_authenticated:
        rooms = DirectMessageRoom.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        )
        return {'dm_rooms': rooms}
    return {'dm_rooms': []}

