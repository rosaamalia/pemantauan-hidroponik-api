from django.urls import path

from . import views

urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.verify_login, name="login"),
    path("verifikasi-kode", views.verifikasi_kode, name="verifikasi_kode"),
    path("kirim-kode", views.kirim_kode, name="kirim_kode"),
]

app_name = "akun"