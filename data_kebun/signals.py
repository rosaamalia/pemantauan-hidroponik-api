from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from kebun.models import Kebun
from .models import DataKebun
from .utils import prediction

@receiver(pre_save, sender=DataKebun)
def set_hasil_rekomendasi(sender, instance, **kwargs):
    if not instance.pk:
        kebun = Kebun.objects.get(id=instance.id_kebun.id)
        path_model = kebun.id_jenis_tanaman.model

        hasil_rekomendasi = prediction(instance.tds, instance.intensitas_cahaya, instance.ph, path_model)
        print(hasil_rekomendasi)

        instance.hasil_rekomendasi = hasil_rekomendasi
    else:
        pass

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
