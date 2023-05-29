from django.contrib import admin
from .models import Akun, KodeVerifikasi

# Register your models here.
@admin.register(Akun)
class AkunAdmin(admin.ModelAdmin):
    list_display = ("id", "nama_pengguna", "username", "foto_profil", "nomor_whatsapp", "terverifikasi", "is_staff", "is_superuser", "created_at", "modified_at")
    search_fields = ("id", "nama_pengguna", "username", "nomor_whatsapp")

@admin.register(KodeVerifikasi)
class KodeVerfifikasiAdmin(admin.ModelAdmin):
    list_display = ("id", "id_akun", "kode", "waktu_kirim", "waktu_kedaluwarsa", "nomor_whatsapp", "created_at", "modified_at")
    search_fields = ("id", "id_akun", "kode", "waktu_kirim", "waktu_kedaluwarsa", "nomor_whatsapp")