from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import DataKebun

@receiver(post_save, sender=DataKebun)
def kirim_data_kebun_terbaru(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "data_kebun_terbaru",
            {
                "type": "get_data_kebun",
            },
        )
