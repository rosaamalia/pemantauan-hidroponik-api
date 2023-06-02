from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_jenis_tanaman, name="get_jenis_tanaman"),
    path("<int:id_jenis_tanaman>", views.jenis_tanaman_berdasarkan_id, name="jenis_tanaman_berdasarkan_id"),
    path("cari", views.cari_jenis_tanaman, name="cari_jenis_tanaman"),
]

app_name = "jenis_tanaman"