from .models import JenisTanaman
from rest_framework import serializers

class JenisTanamanSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenisTanaman
        fields = '__all__'