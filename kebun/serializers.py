from .models import Kebun
from jenis_tanaman.serializers import JenisTanamanSerializer
from rest_framework import serializers

class KebunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kebun
        fields = '__all__'
        
class SemuaKebunSerializer(serializers.ModelSerializer):
    jenis_tanaman = serializers.SerializerMethodField()
    
    class Meta:
        model = Kebun
        fields = ('id', 'id_akun', 'nama_kebun', 'deskripsi', 'latitude', 'longitude', 'alamat', 'jenis_tanaman','created_at', 'modified_at')
        
    def get_jenis_tanaman(self, obj):
        return JenisTanamanSerializer(obj.id_jenis_tanaman).data