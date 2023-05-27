from django.urls import path
from . import views

urlpatterns = [
    path("", views.kebun_disematkan, name="kebun_disematkan")
]

app_name = "kebun_disematkan"