from django.contrib import admin
from .models import DataKebun

# Register your models here.
@admin.register(DataKebun)
class DataKebunAdmin(admin.ModelAdmin):
    list_display = ("id", "id_kebun", "ph", "temperatur", "tds", "intensitas_cahaya", "kelembapan", "ec", "hasil_rekomendasi", "created_at", "modified_at")
    search_fields = ("id", "id_kebun", "ph", "temperatur", "tds", "intensitas_cahaya", "kelembapan", "ec", "hasil_rekomendasi")