from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/data-kebun/terbaru$', consumers.DataKebunConsumer.as_asgi())
]