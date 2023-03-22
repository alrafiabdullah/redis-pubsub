from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('test', consumers.ChatConsumer.as_asgi(), name='test'),
    path('redis/pubsub/<str:room_name>',
         consumers.RedisConsumer.as_asgi(), name='redis_test'),
]
