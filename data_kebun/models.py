from django.db import models
from kebun.models import Kebun

class DataKebun(models.Model):
    id_kebun = models.ForeignKey(Kebun, on_delete=models.CASCADE)
    ph = models.FloatField()
    temperatur = models.FloatField()
    tds = models.FloatField()
    intensitas_cahaya = models.FloatField()
    kelembapan = models.FloatField()
    hasil_rekomendasi = models.CharField(max_length=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.id_kebun, self.created_at)
    
    class Meta:
        app_label = "data_kebun"
        db_table = "data_kebun"
