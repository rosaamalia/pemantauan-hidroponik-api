from django.db import models
from django.contrib.postgres.fields import ArrayField
from akun.models import Akun

class KebunDisematkan(models.Model):
    id_akun = models.OneToOneField(Akun, on_delete=models.CASCADE)
    kebun = ArrayField(models.IntegerField(), default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.id_akun, self.kebun)
    
    class Meta:
        app_label = "kebun_disematkan"
        db_table = "kebun_disematkan"
