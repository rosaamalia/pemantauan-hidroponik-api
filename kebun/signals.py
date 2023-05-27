from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from akun.models import Akun
from kebun.models import Kebun
from .models import DataKebun, Notifikasi
from .utils import prediction
from dotenv import load_dotenv
import os, requests
load_dotenv()

@receiver(pre_save, sender=DataKebun)
def set_hasil_rekomendasi(sender, instance, **kwargs):
    if not instance.pk:
        kebun = Kebun.objects.get(id=instance.id_kebun.id)
        path_model = kebun.id_jenis_tanaman.model

        hasil_rekomendasi = prediction(instance.tds, instance.intensitas_cahaya, instance.ph, path_model)
        instance.hasil_rekomendasi = hasil_rekomendasi
    else:
        pass

def membuat_pesan(parameter, keadaan):
    data = [{ "type": "text", "text": parameter }, { "type": "text", "text": keadaan }]
    return data

def mengirim_pesan_notifikasi(id_notifikasi, data_parameter, nomor_whatsapp):
    print(data_parameter)
    url = os.getenv('WHATSAPP_URL')
    headers = { 'Authorization': 'Bearer ' + os.getenv('WHATSAPP_TOKEN') }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": nomor_whatsapp,
        "type": "template",
        "template": {
            "name": "notifikasi",
            "language": {
                "code": "id"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": data_parameter
                }
            ]
        }
    }

    print(data)

    response = requests.post(url, headers=headers,json=data)
    print(response.json())

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
        print(f"id_kebun {id_kebun}")
        data_akun = Akun.objects.get(id=instance.id_kebun.id_akun.id)
        print(f"data_akun {data_akun.nama_pengguna}")
        data_notifikasi = Notifikasi.objects.get(id_kebun=id_kebun)
        print(f"data_notifikasi {data_notifikasi.id}")

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
            if i == 'ph':
                if instance.ph < data_notifikasi.ph_min:
                    data = membuat_pesan("pH larutan", f"kurang dari {data_notifikasi.ph_min}")
                    parameter.extend(data)
                elif instance.ph > data_notifikasi.ph_min:
                    data = membuat_pesan("pH larutan", f"lebih dari {data_notifikasi.ph_max}")
                    parameter.extend(data)
            elif i == 'temperatur':
                if instance.temperatur < data_notifikasi.temperatur_min:
                    data = membuat_pesan("temperatur udara", f"kurang dari {data_notifikasi.temperatur_min}℃")
                    parameter.extend(data)
                elif instance.temperatur > data_notifikasi.temperatur_min:
                    data = membuat_pesan("temperatur udara", f"lebih dari {data_notifikasi.temperatur_max}℃")
                    parameter.extend(data)
            elif i == 'tds':
                if instance.tds < data_notifikasi.tds_min:
                    data = membuat_pesan("TDS", f"kurang dari {data_notifikasi.tds_min}")
                    parameter.extend(data)
                elif instance.tds > data_notifikasi.tds_min:
                    data = membuat_pesan("TDS", f"lebih dari {data_notifikasi.tds_max}")
                    parameter.extend(data)
            elif i == 'intensitas_cahaya':
                if instance.intensitas_cahaya < data_notifikasi.intensitas_cahaya_min:
                    data = membuat_pesan("intensitas cahaya", f"kurang dari {data_notifikasi.intensitas_cahaya_min}")
                    parameter.extend(data)
                elif instance.intensitas_cahaya > data_notifikasi.intensitas_cahaya_min:
                    data = membuat_pesan("intensitas cahaya", f"lebih dari {data_notifikasi.intensitas_cahaya_max}")
                    parameter.extend(data)
            elif i == 'kelembapan':
                if instance.kelembapan < data_notifikasi.kelembapan_min:
                    data = membuat_pesan("kelembapan udara", f"kurang dari {data_notifikasi.kelembapan_min}")
                    parameter.extend(data)
                elif instance.kelembapan > data_notifikasi.kelembapan_min:
                    data = membuat_pesan("kelembapan udara", f"lebih dari {data_notifikasi.kelembapan_max}")
                    parameter.extend(data)

            mengirim_pesan_notifikasi(data_notifikasi.id, parameter, data_akun.nomor_whatsapp)
            parameter = parameter[:-2]

@receiver(post_save, sender=Kebun)
def membuat_notifikasi(sender, instance, created, **kwargs):
    if created:
        Notifikasi.objects.create(id_kebun=instance)