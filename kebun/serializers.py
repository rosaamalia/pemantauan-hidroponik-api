from .models import Kebun, KebunDisematkan
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
    
class KebunDisematkanSerializer(serializers.ModelSerializer):
    class Meta:
        model = KebunDisematkan
        fields = '__all__'
    
class SemuaKebunDisematkanSerializer(serializers.ModelSerializer):
    kebun = serializers.SerializerMethodField()

    class Meta:
        model = KebunDisematkan
        fields = ('kebun',)
    
    def get_kebun(self, obj):
        daftar_kebun = obj.kebun
        data_kebun_disematkan = []

        for i in daftar_kebun:
            data_kebun = Kebun.objects.get(id=i)
            data_kebun_disematkan.append(SemuaKebunSerializer(instance=data_kebun).data)
        
        return data_kebun_disematkan