import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from giga_chad_app import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "giga_chad_project.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/bci/", consumers.BCIConsumer.as_asgi()),
            path("ws/brain-level/", consumers.BrainLevelConsumer.as_asgi()),
        ])
    ),
})
