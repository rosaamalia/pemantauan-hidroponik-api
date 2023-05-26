from django.urls import path
from . import views

urlpatterns = [
    path("", views.kebun, name="get_post_kebun"),
    path("<int:id_kebun>", views.kebun_berdasarkan_id, name="kebun_berdasarkan_id"),
    path("cari", views.cari_kebun, name="cari_kebun"),
    path("disematkan", views.kebun_disematkan, name="kebun_disematkan")
]

app_name = "kebun"