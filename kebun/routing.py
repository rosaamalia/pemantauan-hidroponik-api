from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path("data-kebun/terbaru/<id_kebun>", consumers.DataKebunConsumer.as_asgi())
]