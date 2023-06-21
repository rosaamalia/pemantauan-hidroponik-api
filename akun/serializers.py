from .models import Akun
from rest_framework import serializers

class AkunSerializer(serializers.ModelSerializer):
    jumlah_kebun = serializers.SerializerMethodField()

    class Meta:
        model = Akun
        fields= ('id', 'nama_pengguna', 'username', 'foto_profil', 'nomor_whatsapp', 'terverifikasi', 'jumlah_kebun', 'created_at', 'modified_at')

    def get_jumlah_kebun(self, obj):
        return self.context.get('jumlah_kebun')
    
    def get_foto_profil(self, obj):
        if obj.foto_profil:
            foto_profil_url = self.context['request'].build_absolute_uri(obj.foto_profil.url)
            return foto_profil_url
        else:
            return None

class UpdateAkunSerializer(serializers.ModelSerializer):
    nomor_whatsapp = serializers.CharField(read_only=True)
    terverifikasi = serializers.BooleanField(read_only=True)
    jumlah_kebun = serializers.SerializerMethodField()

    class Meta:
        model = Akun
        fields= ('id', 'nama_pengguna', 'username', 'foto_profil', 'nomor_whatsapp', 'terverifikasi', 'jumlah_kebun', 'created_at', 'modified_at')

    def get_jumlah_kebun(self, obj):
        return self.context.get('jumlah_kebun')
    
    def get_foto_profil(self, obj):
        if obj.foto_profil:
            foto_profil_url = self.context['request'].build_absolute_uri(obj.foto_profil.url)
            return foto_profil_url
        else:
            return None

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Akun
        fields = ('id', 'nama_pengguna', 'username', 'foto_profil', 'password', 'nomor_whatsapp', 'terverifikasi', 'created_at', 'modified_at')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        # Mengecek apakah username sudah ada di database
        if Akun.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError()

        # Mengecek apakah nomor_whatsapp sudah ada di database
        if Akun.objects.filter(nomor_whatsapp=data['nomor_whatsapp']).exists():
            raise serializers.ValidationError()

        return data