from django.db import models
from akun.models import Akun
from jenis_tanaman.models import JenisTanaman

class Kebun(models.Model):
    id_akun = models.ForeignKey(Akun, on_delete=models.CASCADE)
    id_jenis_tanaman = models.ForeignKey(JenisTanaman, on_delete=models.CASCADE)
    nama_kebun = models.CharField(max_length=50, unique=True)
    deskripsi = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    alamat = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_kebun
    
    class Meta:
        app_label = "kebun"
        db_table = "kebun"
