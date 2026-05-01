"""ASGI 入口，支持 HTTP 与 WebSocket。"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

from ai_services.auth import QueryStringJWTAuthMiddlewareStack
from ai_services.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": QueryStringJWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
