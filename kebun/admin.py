from django.contrib import admin
from .models import Kebun, DataKebun, Notifikasi, DetailKirimNotifikasi

# Register your models here.
@admin.register(Kebun)
class KebunAdmin(admin.ModelAdmin):
    list_display = ("id", "nama_kebun", "id_akun", "id_jenis_tanaman", "nama_kebun", "deskripsi", "alamat", "created_at", "modified_at")
    search_fields = ("id", "nama_kebun", "id_akun", "id_jenis_tanaman", "nama_kebun", "deskripsi", "alamat")

@admin.register(DataKebun)
class DataKebunAdmin(admin.ModelAdmin):
    list_display = ("id", "id_kebun", "ph", "temperatur", "tds", "intensitas_cahaya", "kelembapan", "hasil_rekomendasi", "created_at", "modified_at")
    search_fields = ("id", "id_kebun", "ph", "temperatur", "tds", "intensitas_cahaya", "kelembapan", "hasil_rekomendasi")

@admin.register(Notifikasi)
class NotifikasiAdmin(admin.ModelAdmin):
    list_display = ("id", "id_kebun", "ph_min", "ph_max", "temperatur_min", "temperatur_max", "tds_min", "tds_max", "intensitas_cahaya_min", "intensitas_cahaya_max", "kelembapan_min", "kelembapan_max", "created_at", "modified_at")
    search_fields = ("id", "id_kebun", "ph_min", "ph_max", "temperatur_min", "temperatur_max", "tds_min", "tds_max", "intensitas_cahaya_min", "intensitas_cahaya_max", "kelembapan_min", "kelembapan_max", "created_at", "modified_at")

@admin.register(DetailKirimNotifikasi)
class DetailKirimNotifikasiAdmin(admin.ModelAdmin):
    list_display = ("id", "id_notifikasi", "pesan", "created_at", "modified_at")
    search_fields = ("id", "id_notifikasi", "pesan", "created_at", "modified_at")
