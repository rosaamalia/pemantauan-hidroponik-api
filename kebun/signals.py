from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from akun.models import Akun
from kebun.models import Kebun
from .models import DataKebun, Notifikasi, DetailKirimNotifikasi
from .utils import prediction, membuat_pesan, mengirim_pesan_notifikasi

@receiver(pre_save, sender=DataKebun)
def set_hasil_rekomendasi(sender, instance, **kwargs):
    if not instance.pk:
        kebun = Kebun.objects.get(id=instance.id_kebun.id)
        path_model = kebun.id_jenis_tanaman.model

        hasil_rekomendasi = prediction(instance.tds, instance.intensitas_cahaya, instance.ph, path_model)
        instance.hasil_rekomendasi = hasil_rekomendasi
    else:
        pass

@receiver(post_save, sender=DataKebun)
def kirim_data_kebun_terbaru(sender, instance, created, **kwargs):
    if created:
        # Mengirim data terbaru ke client
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "data_kebun_terbaru",
            {
                "type": "get_data_kebun",
            },
        )

        # Mengecek dan mengirim notifikasi
        id_kebun = instance.id_kebun.id
        data_akun = Akun.objects.get(id=instance.id_kebun.id_akun.id)
        data_notifikasi = Notifikasi.objects.get(id_kebun=id_kebun) # Dikirim untuk membuat detail kirim notifikasi
        detail_kirim_notifikasi = DetailKirimNotifikasi.objects.filter(id_notifikasi=data_notifikasi.id) # Jika sudah ada, waktunya mau dibandingin

        parameter = [
            {
                "type": "text",
                "text": data_akun.nama_pengguna
            },
            {
                "type": "text",
                "text": id_kebun
            },
        ]

        macam_parameter = ['ph', 'temperatur', 'tds', 'intensitas_cahaya', 'kelembapan']

        # Mengecek data yang masuk dengan batas parameter
        for i in macam_parameter:
            min_value = getattr(data_notifikasi, f"{i}_min")
            max_value = getattr(data_notifikasi, f"{i}_max")
            data_kebun = getattr(instance, i)
            delta_waktu = timezone.timedelta(minutes=15)

            if data_kebun < min_value:
                data = membuat_pesan(i.upper(), f"kurang dari {min_value}")
                parameter.extend(data)
            elif data_kebun > min_value:
                data = membuat_pesan(i.upper(), f"lebih dari {max_value}")
                parameter.extend(data)
            
            # Dicek apakah pesan yang sama (yang akan dikirim) sudah melewati 15 menit
            if detail_kirim_notifikasi.filter(pesan=parameter).exists():
                waktu = detail_kirim_notifikasi.filter(pesan=parameter).order_by("-created_at").first()
                if (timezone.now() - waktu.created_at) > delta_waktu:
                    mengirim_pesan_notifikasi(data_notifikasi, parameter, data_akun.nomor_whatsapp)
            else:
                mengirim_pesan_notifikasi(data_notifikasi, parameter, data_akun.nomor_whatsapp)

            parameter.pop()
            parameter.pop()

@receiver(post_save, sender=Kebun)
def membuat_notifikasi(sender, instance, created, **kwargs):
    if created:
        Notifikasi.objects.create(id_kebun=instance)