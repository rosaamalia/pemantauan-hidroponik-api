from rest_framework import serializers
from .models import KebunDisematkan
from kebun.models import Kebun
from kebun.serializers import SemuaKebunSerializer

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