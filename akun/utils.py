from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied

def verifikasi_id_akun(id_jwt, id_akun):
    # Memastikan seorang pengguna hanya mengakses data miliknya saja
    if id_jwt != id_akun:
        raise PermissionDenied()