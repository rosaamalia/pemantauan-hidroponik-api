from django.contrib import admin
from .models import JenisTanaman
from .forms import JenisTanamanForm

# Register your models here.
@admin.register(JenisTanaman)
class JenisTanamanAdmin(admin.ModelAdmin):
    list_display = ("id", "nama_tanaman", "deskripsi", "model", "created_at", "modified_at")
    search_fields = ("id", "nama_tanaman", "deskripsi", "teks_artikel")
    form = JenisTanamanForm
