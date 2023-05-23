from rest_framework import serializers
from .models import DataKebun

class DataKebunSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataKebun
        fields = "__all__"