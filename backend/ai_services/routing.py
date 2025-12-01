"""AI 服务 WebSocket 路由。"""

from django.urls import path

from .consumers import StudentAIChatConsumer


websocket_urlpatterns = [
    path("ws/student/ai/chat", StudentAIChatConsumer.as_asgi()),
]
