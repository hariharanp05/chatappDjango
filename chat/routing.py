"""
WebSocket URL routing for the chat application.
Maps WebSocket paths to their corresponding ASGI consumers.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket endpoint for public chat rooms (e.g., /ws/chat/general/)
    re_path(r'^ws/chat/(?P<room_name>[\w-]+)/$', consumers.ChatConsumer.as_asgi()),

    # WebSocket endpoint for private direct message rooms (e.g., /ws/private/dm_10_11/)
    re_path(r'^ws/private/(?P<room_name>[\w-]+)/$', consumers.PrivateChatConsumer.as_asgi()),
]
