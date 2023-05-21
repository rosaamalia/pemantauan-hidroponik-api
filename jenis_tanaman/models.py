from django.db import models

class JenisTanaman(models.Model):
    nama_tanaman = models.CharField(max_length=50, unique=True)
    foto = models.CharField(max_length=256)
    deskripsi = models.CharField(max_length=80)
    teks_artikel = models.TextField()
    model = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_tanaman
    
    class Meta:
        app_label = "jenis_tanaman"
        db_table = "jenis_tanaman"
    