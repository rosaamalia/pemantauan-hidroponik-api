from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Akun, KodeVerifikasi
from .serializers import AkunSerializer

import os
import datetime
import requests
import random
from dotenv import load_dotenv
load_dotenv()

def generate_kode():
    # Membuat string kode verifikasi yang terdiri dari 5 angka
    number_string = ''.join(random.choices('0123456789', k=5))
    return number_string

def kirim_kode_whatsapp(nomor_whatsapp):
    # Mengirim kode verifikasi menggunakan pesan whatsapp
    # Jika kode berhasil dikirim, akan mengembalikan kode verifikasi dan waktu pengiriman

    kode = generate_kode()
    url = os.getenv('WHATSAPP_URL')
    headers = { 'Authorization': 'Bearer ' + os.getenv('WHATSAPP_TOKEN') }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": nomor_whatsapp,
        "type": "template",
        "template": {
            "name": "kode_verifikasi",
            "language": {
                "code": "id"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": kode
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": kode
                        }
                    ]
                }
            ]
        }
    }
    
    response = requests.post(url, headers=headers,json=data)
    data = response.json()

    if "error" in data:
        return False, None
    else:
        return kode, datetime.datetime.now()

@api_view(['POST'])
@permission_classes([AllowAny])
def verifikasi_kode(request, konteks=None):
    # Verifikasi kode yang dimasukkan oleh pengguna
    kode = request.data.get("kode")

    # Memeriksa kode dari database
    kode_db = KodeVerifikasi.objects.filter(kode=kode)

    if not kode_db.exists():
        return Response({"error": "Kode verifikasi salah."}, status=status.HTTP_400_BAD_REQUEST)
    
    kode_db = kode_db.first()
    if timezone.now() > kode_db.waktu_kadaluarsa:
        return Response({"error": "Kode verifikasi sudah kadaluarsa."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Jika kode ada dan belum kadaluarsa
    if konteks == None:
        # Update data akun menjadi terverifikasi
        Akun.objects.filter(id=kode_db.id_akun.id).update(terverifikasi=True)
        
    return Response({"message": "Kode verifikasi berhasil diverifikasi."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def kirim_kode(request):
    nomor_whatsapp = request.data.get('nomor_whatsapp')
    kode_verifikasi, waktu_kirim = kirim_kode_whatsapp(nomor_whatsapp)

    # Menyimpan kode verifikasi baru
    akun = Akun.objects.get(nomor_whatsapp=nomor_whatsapp)
    KodeVerifikasi.objects.create(id_akun=akun, kode=kode_verifikasi, waktu_kirim=waktu_kirim)
    
    return Response({"message": "Kode verifikasi telah dikirimkan ke nomor whatsapp Anda."}, status=status.HTTP_200_OK)

# Register
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data.copy()
    data["password"] = request.data["kata_sandi"]
    del data["kata_sandi"]

    serializer = AkunSerializer(data=data)

    if serializer.is_valid():
        # Kirim kode verifikasi
        kode_verifikasi, waktu_kirim = kirim_kode_whatsapp(nomor_whatsapp=data["nomor_whatsapp"])

        if kode_verifikasi != False:
            pass
        else:
            return Response({"error": "Kesalahan pada pengiriman kode verifikasi"}, status=status.HTTP_409_CONFLICT)
        
        # Melakukan hash pada kata sandi dan menyimpan data akun
        hashed_password = make_password(data['password'])
        serializer.validated_data['password'] = hashed_password
        akun = serializer.save()

        # Menyimpan kode verifikasi
        KodeVerifikasi.objects.create(id_akun=akun, kode=kode_verifikasi, waktu_kirim=waktu_kirim)

        # Verifikasi kode akan dilakukan setelah pengguna mengirimkan kode ke server
        # dan status data pengguna akan menjadi terverifikasi

        # Generate token untuk akun
        refresh = RefreshToken.for_user(akun)

        return Response({
            "message": "Akun berhasil didaftarkan",
            "data": serializer.data,
            "token" : {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# Register
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login(request):
    if request.headers.get('Authorization') and 'Bearer' in request.headers['Authorization']:
        # Request dengan Bearer token
        refresh_token = request.headers['Authorization'].split()[1]
        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            return Response({
                    "token": {
                        'refresh': refresh_token,
                        'access': access_token
                    }
                }, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Request dengan basic authentication
        username = request.data.get('username')
        password = request.data.get('kata_sandi')

        if not username or not password:
            return Response({'error': 'Username dan kata sandi harus diisi'}, status=status.HTTP_400_BAD_REQUEST)
    
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Generate token baru
            login(request, user)
            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                    "message": "Login berhasil",
                    "token": {
                        'refreh': refresh_token, 
                        'access': access_token
                    }
                }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Username atau kata sandi salah.'}, status=status.HTTP_400_BAD_REQUEST)