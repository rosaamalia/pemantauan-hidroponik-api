from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password

class AkunManager(BaseUserManager):
    def create_user(self, nama_pengguna, username, password, nomor_whatsapp, **extra_fields):
        if not nama_pengguna:
            raise ValueError("Nama pengguna harus diisi.")
        if not username:
            raise ValueError("Username harus diisi.")
        if not password:
            raise ValueError("Kata sandi harus diisi.")
        if not nomor_whatsapp:
            raise ValueError("Nomor WhatsApp sandi harus diisi.")
        
        user = self.model(
            nama_pengguna=nama_pengguna,
            username=username,
            nomor_whatsapp=nomor_whatsapp,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nama_pengguna, username, password, nomor_whatsapp, **extra_fields):
        user = self.create_user(
            nama_pengguna=nama_pengguna,
            username=username,
            password=password,
            nomor_whatsapp=nomor_whatsapp,
            **extra_fields
        )
        
        user.is_superuser = True
        user.is_staff = True
        user.terverifikasi = True
        user.save(using=self._db)
        return user

class Akun(AbstractBaseUser):
    nama_pengguna = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    foto_profil = models.CharField(max_length=255, blank=True)
    nomor_whatsapp = models.CharField(max_length=15, unique=True)
    terverifikasi = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nama_pengguna', 'nomor_whatsapp']
    
    objects = AkunManager()
    
    def __str__(self):
        return self.nama_pengguna
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    class Meta:
        app_label = "akun"
        db_table = "akun"
    
class KodeVerifikasi(models.Model):
    id_akun = models.ForeignKey(Akun, on_delete=models.CASCADE)
    kode = models.CharField(max_length=5)
    waktu_kirim = models.DateTimeField()
    waktu_kadaluarsa = models.DateTimeField()
    nomor_whatsapp = models.CharField(max_length=15, default="0")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return "{0} - {1}".format(self.id_akun, self.kode)
    
    class Meta:
        app_label = "akun"
        db_table = "kode_verifikasi"