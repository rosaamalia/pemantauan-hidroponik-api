from django.contrib import admin
from .models import Kebun

# Register your models here.
@admin.register(Kebun)
class KebunAdmin(admin.ModelAdmin):
    list_display = ("id", "nama_kebun", "id_akun", "id_jenis_tanaman", "nama_kebun", "deskripsi", "alamat", "created_at", "modified_at")
    search_fields = ("id", "nama_kebun", "id_akun", "id_jenis_tanaman", "nama_kebun", "deskripsi", "alamat")