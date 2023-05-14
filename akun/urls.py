from django.urls import path

from . import views

urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.verify_login, name="login"),
]

app_name = "akun"