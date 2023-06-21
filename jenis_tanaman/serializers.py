from .models import JenisTanaman
from rest_framework import serializers

class JenisTanamanSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenisTanaman
        fields = '__all__'
    
    def get_foto(self, obj):
        if obj.foto:
            foto_path = self.context['request'].build_absolute_uri(obj.foto.url)
            return foto_path
        else:
            return None
    
    def get_model(self, obj):
        if obj.model:
            model_path = self.context['request'].build_absolute_uri(obj.model.url)
            return model_path
        else:
            return None