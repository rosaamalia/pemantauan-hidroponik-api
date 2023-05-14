from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import KodeVerifikasi

@receiver(pre_save, sender=KodeVerifikasi)
def set_waktu_kadaluarsa(sender, instance, **kwargs):
    if not instance.pk:
        # instance belum disimpan, berarti ini adalah insert pertama kali
        instance.waktu_kadaluarsa = instance.waktu_kirim + timezone.timedelta(minutes=5)
    else:
        # instance sudah pernah disimpan sebelumnya, berarti ini adalah update
        # waktu_kadaluarsa tidak perlu diubah karena hanya ingin berubah saat insert saja
        pass