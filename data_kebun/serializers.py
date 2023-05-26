from rest_framework import serializers
from .models import DataKebun
from .utils import nama_hari, nama_bulan

import calendar
from datetime import datetime

class DataKebunSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataKebun
        fields = "__all__"

class GetDataKebunSerializer(serializers.ModelSerializer):
    tanggal = serializers.SerializerMethodField()
    waktu = serializers.SerializerMethodField()

    class Meta:
        model = DataKebun
        fields = ("id", "id_kebun", "tanggal", "waktu", "ph", "temperatur", "tds", "intensitas_cahaya", "kelembapan", "hasil_rekomendasi")
    
    def get_tanggal(self, obj):
        tanggal_waktu = datetime.fromisoformat(str(obj.created_at))
        hari = calendar.day_name[tanggal_waktu.weekday()]
        bulan = calendar.month_name[tanggal_waktu.month]

        return "{0}, {1} {2} {3}".format(nama_hari(hari), tanggal_waktu.strftime("%d"), nama_bulan(bulan), tanggal_waktu.strftime("%Y"))
    
    def get_waktu(self, obj):
        tanggal_waktu = datetime.fromisoformat(str(obj.created_at))

        return tanggal_waktu.strftime("%H:%M:%S")