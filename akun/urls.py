from django.urls import path

from . import views

urlpatterns = [
    # Proses Otentikasi
    path("auth/register", views.register, name="register"),
    path("auth/login", views.verify_login, name="login"),

    # Proses Verifikasi Nomor WhatsApp
    path("verifikasi/kirim-kode", views.kirim_kode, name="kirim_kode"),
    path("verifikasi/kirim-kode/update-nomor-whatsapp", views.kirim_kode_update_nomor_whatsapp, name="kirim_kode_update_nomor_whatsapp"),
    path("verifikasi/verifikasi-kode-registrasi", views.verifikasi_kode_registrasi, name="verifikasi_kode_registrasi"),
    path("verifikasi/verifikasi-kode-nomor-whatsapp", views.verifikasi_kode_update_nomor_whatsapp, name="verifikasi_kode_update_nomor_whatsapp"),

    # Akun
    path("akun", views.akun_berdasarkan_id, name="akun_berdasarkan_id"),
    path("akun/update-kata-sandi", views.update_kata_sandi, name="update_kata_sandi"),
]

app_name = "akun"