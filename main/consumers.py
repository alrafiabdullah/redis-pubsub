import json
import asyncio
import aioredis

from channels.generic.websocket import AsyncWebsocketConsumer

from django.conf import settings


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "test_room"
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        res = "Pong"

        if "hello" in message.lower():
            res = "Hi, nice to meet you!"

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': res
        }))


class RedisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        await self.accept()
        self.redis_t = await aioredis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.redis = self.redis_t.pubsub()

        await self.redis.subscribe(self.room_name)

        # retrieve last 30 messages
        messages = await self.redis_t.lrange(self.room_name, -10, -1)

        # messages = await self.redis_t.lrange(self.room_name, 0, 50)

        for msg in messages:
            await self.send(text_data=json.dumps({
                'message': msg
            }))

        asyncio.ensure_future(self.listen_for_redis_messages())

    async def listen_for_redis_messages(self):
        async for message in self.redis.listen():
            if message['type'] == 'message':
                await self.chat_message({"message": message['data']})

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.redis_t.publish(self.room_name, message)
        await self.store_messages({"message": message})

    async def chat_message(self, event):
        msg = event['message']

        await self.send(text_data=json.dumps({
            'message': msg
        }))

    async def store_messages(self, event):
        msg = event['message']
        await self.redis_t.rpush(self.room_name, msg)

    async def disconnect(self, close_code):
        await self.redis.unsubscribe(self.room_name)
        await self.redis.close()
