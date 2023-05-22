from channels.db import database_sync_to_async
from djangochannelsrestframework import permissions
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer, action
from djangochannelsrestframework.mixins import ListModelMixin
from djangochannelsrestframework.observer import model_observer
from rest_framework_simplejwt.tokens import AccessToken

from .models import DataKebun
from .serializers import DataKebunSerializer

from urllib.parse import parse_qs

class DataKebunConsumer(ListModelMixin, GenericAsyncAPIConsumer):
    queryset = DataKebun.objects.all()
    serializer_class = DataKebunSerializer
    permission = (permissions.IsAuthenticated,)
    # authentication = [JWTAuthentication,]

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()

    @model_observer(DataKebun)
    async def model_change(self, message, observer=None, **kwargs):
        await self.send_json(message)

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        return dict(data=DataKebunSerializer(instance=instance).data, action=action.value)

    @action()
    async def get_latest_data_kebun(self, id_kebun):
        # Dapatkan ID kebun dari parameter query
        if id_kebun:
            try:
                # # Dapatkan ID pengguna dari token JWT
                # headers = self.scope['headers']
                # for header_name, header_value in headers:
                #     if header_name == b'authorization':
                #         # Ambil token JWT dari header
                #         token = header_value.decode().split(' ')[1]
                #         break

                # decoded_token = AccessToken(token)
                # id_user = decoded_token['id']

                # Dapatkan kebun terbaru berdasarkan ID kebun
                data_kebun = await self.get_latest_data_kebun_async(id_kebun)
                serializer = DataKebunSerializer(data_kebun)

                # Kirim data kebun terbaru ke klien melalui WebSocket
                await self.send_json_response(serializer.data)
            except DataKebun.DoesNotExist:
                # Tolak permintaan jika kebun tidak ditemukan
                await self.send_json_response({'detail': 'Kebun not found'}, status=404)
    
    @database_sync_to_async
    def get_latest_data_kebun_async(self, id_kebun):
        # Dapatkan kebun terbaru berdasarkan ID kebun dan ID pengguna
        return DataKebun.objects.filter(id_kebun__id=id_kebun).order_by('-created_at').first()

