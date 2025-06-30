import json
import os
import base64
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, DirectMessage, DirectMessageRoom


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            username = data.get('username', '')
            profile_pic = data.get('profile_pic', '')
            room = data.get('room', '')
            file_info = data.get('file')
            file_url = await self.save_file(file_info) if file_info else None
            timestamp = datetime.now().strftime('%H:%M')

            await self.save_message(message, username, profile_pic, room, file_url)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'profile_pic': profile_pic,
                    'room': room,
                    'file_url': file_url or '',
                    'timestamp': timestamp,
                }
            )
        except Exception as e:
            print(f"[ChatConsumer Error] {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'profile_pic': event['profile_pic'],
            'room': event['room'],
            'file_url': event['file_url'],
            'timestamp': event.get('timestamp', '')
        }))

    @database_sync_to_async
    def save_file(self, file_info):
        try:
            name = file_info['name']
            data = file_info['data']
            _, file_data = data.split(';base64,')
            unique_name = datetime.now().strftime('%Y%m%d%H%M%S_') + name
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, unique_name)
            relative_path = os.path.join('uploads', unique_name)

            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(file_data))

            return f'/media/{relative_path}'
        except Exception as e:
            print(f"[Public Chat File Error] {e}")
            return None

    @database_sync_to_async
    def save_message(self, message, username, profile_pic, room, file_url):
        try:
            Message.objects.create(
                message_content=message,
                username=username,
                profile_pic=profile_pic,
                room=room,
                file=file_url
            )
        except Exception as e:
            print(f"[Public Chat Message Save Error] {e}")


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'private_chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            username = data.get('username', '')
            room_name = data.get('room', '')  # dm_<id1>_<id2>
            profile_pic = data.get('profile_pic', '')
            file_info = data.get('file')

            file_url = await self.save_file(file_info) if file_info else None
            timestamp = datetime.now().strftime('%H:%M')

            await self.save_private_message(message, username, room_name, file_url, profile_pic)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'room': room_name,
                    'file_url': file_url or '',
                    'timestamp': timestamp,
                    'profile_pic': profile_pic or ''
                }
            )
        except Exception as e:
            print(f"[PrivateChatConsumer Error] {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'room': event['room'],
            'file_url': event['file_url'],
            'timestamp': event.get('timestamp', ''),
            'profile_pic': event.get('profile_pic', '')
        }))

    @database_sync_to_async
    def save_file(self, file_info):
        try:
            name = file_info['name']
            data = file_info['data']
            _, file_data = data.split(';base64,')
            unique_name = datetime.now().strftime('%Y%m%d%H%M%S_') + name
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'dm')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, unique_name)
            relative_path = os.path.join('uploads', 'dm', unique_name)

            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(file_data))

            return f'/media/{relative_path}'
        except Exception as e:
            print(f"[Private Chat File Error] {e}")
            return None

    @database_sync_to_async
    def save_private_message(self, message, username, room_name, file_url, profile_pic):
        try:
            user = User.objects.get(username=username)

            # Validate room name format: "dm_<user1_id>_<user2_id>"
            parts = room_name.split('_')
            if len(parts) != 3 or parts[0] != 'dm':
                print(f"[Room Error] Invalid room format: {room_name}")
                return

            uid1, uid2 = int(parts[1]), int(parts[2])
            user1 = User.objects.get(id=uid1)
            user2 = User.objects.get(id=uid2)

            room = DirectMessageRoom.get_or_create_room(user1, user2)
            DirectMessage.objects.create(
                room=room,
                sender=user,
                message_content=message,
                file=file_url,
                profile_pic=profile_pic or None
            )
        except Exception as e:
            print(f"[Private Chat Message Save Error] {e}")
