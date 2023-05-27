from django.contrib import admin
from .models import KebunDisematkan

# Register your models here.
@admin.register(KebunDisematkan)
class KebunDisematkanAdmin(admin.ModelAdmin):
    list_display = ("id", "id_akun", "kebun", "created_at", "modified_at")
    search_fields = ("id", "id_akun", "kebun", "created_at", "modified_at")