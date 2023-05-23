from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from .models import DataKebun
from .serializers import DataKebunSerializer

class DataKebunConsumer(AsyncWebsocketConsumer):
    async def connect (self):
        print('connected')
        await self.accept()
        await self.channel_layer.group_add("data_kebun_terbaru", self.channel_name)

    async def disconnect(self, code):
        print(f'connection closed with: {code}')
        await self.channel_layer.group_discard("data_kebun_terbaru", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        id_kebun = text_data_json['id_kebun']

        data_kebun = await self.get_data_kebun_terbaru(id_kebun)
        
        await self.send(text_data=json.dumps({
            'message': data_kebun
        }))

    async def get_data_kebun(self, event):
        id_kebun = self.scope["url_route"]["kwargs"]["id_kebun"]
        print(id_kebun)

        data_kebun = await self.get_data_kebun_terbaru(id_kebun)

        await self.send(text_data=json.dumps({
            'message': data_kebun
        }))
    
    @database_sync_to_async
    def get_data_kebun_terbaru(self, id_kebun):
        data = DataKebun.objects.filter(id_kebun__id=id_kebun).order_by("-created_at").first()
        serializer = DataKebunSerializer(instance=data)

        return serializer.data