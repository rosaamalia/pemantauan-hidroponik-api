from django.urls import path
from . import views

urlpatterns = [
    # Kebun
    path("", views.kebun, name="get_post_kebun"),
    path("<int:id_kebun>", views.kebun_berdasarkan_id, name="kebun_berdasarkan_id"),
    path("cari", views.cari_kebun, name="cari_kebun"),
    
    # Data Kebun
    path("test", views.index, name="index"),
    path("<int:id_kebun>/data", views.data_kebun_berdasarkan_id_kebun, name="data_kebun_berdasarkan_id_kebun"),
    path("<int:id_kebun>/data/rata-rata", views.data_kebun_rata_rata, name="data_kebun_rata_rata"),

    # Notifikasi
    path("<int:id_kebun>/notifikasi", views.notifikasi, name="notifikasi"),
]

app_name = "kebun"