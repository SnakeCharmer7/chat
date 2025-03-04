import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from asgiref.sync import sync_to_async


class ChatroomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await self.get_chat_history()
        await self.send(text_data=json.dumps({"history": messages}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        username = data["username"]

        user = await self.get_user(username)
        new_message = Message(user=user, content=message)
        await self.save_message(new_message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def get_chat_history(self):
        messages = await self.get_last_messages(10)
        return [{"username": msg.user.username, "message": msg.content} for msg in messages]

    @staticmethod
    async def get_user(username):
        return await User.objects.filter(username=username).afirst()

    @staticmethod
    async def save_message(message):
        await message.asave()

    @staticmethod
    async def get_last_messages(count):
        return await sync_to_async(list)(Message.objects.all().order_by("-timestamp")[:count])
