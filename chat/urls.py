from django.urls import path
from . import views as chat_views

urlpatterns = [
    # Home page with room join form and list of private chats
    path('', chat_views.chat_home, name='chat-home'),
    path("ajax/user-search/", chat_views.ajax_user_search, name="ajax-user-search"),


    # Public Chat Room
    path('<str:room_name>/', chat_views.chat_room, name='chat_room'),

    # User Profile
    path('user/<str:username>/', chat_views.user_profile, name='user_profile'),

    # Private Messaging (Direct Messages)
    path('direct-messages/', chat_views.direct_messages, name='direct_messages'),
    path('private-chat/<int:user_id>/', chat_views.private_chat_room, name='private_chat_room'),

    # Message Requests
    path('profile/<int:user_id>/send-request/', chat_views.send_message_request, name='send_message_request'),
    path('accept-request/<int:request_id>/', chat_views.accept_message_request, name='accept_message_request'),
    path('notifications/', chat_views.notifications, name='notifications'),

    # Block/Unblock Users
    path('block/<int:user_id>/', chat_views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', chat_views.unblock_user, name='unblock_user'),
    path('blocked-users/', chat_views.blocked_users, name='blocked_users'),
]
