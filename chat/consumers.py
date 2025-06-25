import json
import os
import base64
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        username = text_data_json.get('username', '')
        profile_pic = text_data_json.get('profile_pic', '')
        room = text_data_json.get('room', '')
        file_info = text_data_json.get('file', None)

        file_url = None
        if file_info:
            file_url = await self.save_file(file_info)

        await self.save_message(message, username, profile_pic, room, file_url)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'profile_pic': profile_pic,
                'room': room,
                'file_url': file_url
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'profile_pic': event['profile_pic'],
            'room': event['room'],
            'file_url': event['file_url'] or '',
        }))

    @database_sync_to_async
    def save_file(self, file_info):
        try:
            name = file_info['name']
            data = file_info['data']

            # Split the base64 string
            format, imgstr = data.split(';base64,')
            ext = name.split('.')[-1]
            unique_name = datetime.now().strftime('%Y%m%d%H%M%S_') + name
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_name)
            relative_path = f'uploads/{unique_name}'

            # Make sure the uploads folder exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the file
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(imgstr))
                
            return f'/media/{relative_path}'

        except Exception as e:
            print(f"File saving error: {e}")
            return None

    @database_sync_to_async
    def save_message(self, message, username, profile_pic, room, file_url):
        Message.objects.create(
            message_content=message,
            username=username,
            profile_pic=profile_pic,
            room=room,
            file=file_url
        )
