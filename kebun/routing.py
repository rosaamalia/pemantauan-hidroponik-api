from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path("kebun/<id_kebun>/data/terbaru", consumers.DataKebunConsumer.as_asgi())
]