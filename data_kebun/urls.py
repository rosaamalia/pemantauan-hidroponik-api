from django.urls import path
from . import views

urlpatterns = [
    path("test", views.index, name="index"),
    path("", views.data_kebun_berdasarkan_id_kebun, name="data_kebun_berdasarkan_id_kebun"),
]

app_name = "data_kebun"