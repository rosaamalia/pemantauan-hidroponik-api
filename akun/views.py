from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from .models import Akun, KodeVerifikasi
from .serializers import RegisterSerializer, AkunSerializer, UpdateAkunSerializer
from .utils import kirim_kode_whatsapp, cek_numerik
from kebun.models import Kebun

@api_view(['POST'])
@permission_classes([AllowAny])
def verifikasi_kode_registrasi(request):
    # Verifikasi kode registrasi
    kode = request.data.get("kode")

    # Memeriksa kode dari database
    kode_db = KodeVerifikasi.objects.filter(kode=kode)

    if not kode_db.exists():
        return Response({"detail": "Kode verifikasi salah."}, status=status.HTTP_400_BAD_REQUEST)
    
    kode_db = kode_db.first()
    if timezone.now() > kode_db.waktu_kedaluwarsa:
        return Response({"detail": "Kode verifikasi sudah kedaluwarsa."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Jika kode ada dan belum kedaluwarsa
    # Update data akun menjadi terverifikasi
    Akun.objects.filter(id=kode_db.id_akun.id).update(terverifikasi=True)
        
    return Response({"message": "Kode verifikasi berhasil diverifikasi."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def kirim_kode(request):
    nomor_whatsapp = request.data.get('nomor_whatsapp')

    cek = cek_numerik(nomor_whatsapp)
    if cek == False:
        return Response({"detail": "Nomor whatsapp tidak valid."}, status=status.HTTP_400_BAD_REQUEST)
    
    kode_verifikasi, waktu_kirim = kirim_kode_whatsapp(nomor_whatsapp)

    # Menyimpan kode verifikasi baru
    akun = Akun.objects.get(nomor_whatsapp=nomor_whatsapp)
    KodeVerifikasi.objects.create(id_akun=akun, kode=kode_verifikasi, waktu_kirim=waktu_kirim, nomor_whatsapp=nomor_whatsapp)
    
    return Response({"message": "Kode verifikasi telah dikirimkan ke nomor whatsapp Anda."}, status=status.HTTP_200_OK)

# Register
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data.copy()
    if "kata_sandi" in request.data:
        data["password"] = request.data["kata_sandi"]
        del data["kata_sandi"]
    elif "nomor_whatsapp" in request.data:
        cek = cek_numerik(data["nomor_whatsapp"])
        if cek == False:
            return Response({"detail": "Nomor whatsapp tidak valid."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RegisterSerializer(data=data)

    if serializer.is_valid():
        # Kirim kode verifikasi
        kode_verifikasi, waktu_kirim = kirim_kode_whatsapp(nomor_whatsapp=data["nomor_whatsapp"])

        if kode_verifikasi != False:
            pass
        else:
            return Response({"detail": "Kesalahan pada pengiriman kode verifikasi"}, status=status.HTTP_409_CONFLICT)
        
        # Melakukan hash pada kata sandi dan menyimpan data akun
        hashed_password = make_password(data['password'])
        serializer.validated_data['password'] = hashed_password
        akun = serializer.save()

        # Menyimpan kode verifikasi
        KodeVerifikasi.objects.create(id_akun=akun, kode=kode_verifikasi, waktu_kirim=waktu_kirim, nomor_whatsapp=data["nomor_whatsapp"])

        # Verifikasi kode akan dilakukan setelah pengguna mengirimkan kode ke server
        # dan status data pengguna akan menjadi terverifikasi

        # Menambahkan data jumlah_kebun pada response
        data_response = serializer.data
        data_response['jumlah_kebun'] = 0

        # Generate token untuk akun
        refresh = RefreshToken.for_user(akun)

        return Response({
            "message": "Akun berhasil didaftarkan",
            "data": data_response,
            "token" : {
                "refresh": str(refresh.access_token),
                "access": str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# Login
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
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Request dengan basic authentication
        username = request.data.get('username')
        password = request.data.get('kata_sandi')

        if not username or not password:
            return Response({'detail': 'Username dan kata sandi harus diisi'}, status=status.HTTP_400_BAD_REQUEST)
    
        user = authenticate(request, username=username, password=password)

        if user is not None:
            data_akun = {
                "id": user.id,
                "nama_pengguna": user.nama_pengguna,
                "username": user.username,
                "foto_profil": user.foto_profil,
                "nomor_whatsapp": user.nomor_whatsapp,
                "terverifikasi": user.terverifikasi,
                "jumlah_kebun": 0,
                "created_at": user.created_at,
                "modified_at": user.modified_at
            }
            
            # Generate token baru
            login(request, user)
            refresh = RefreshToken.for_user(user)

            refresh_token = str(refresh.access_token)
            access_token = str(refresh)

            return Response({
                    "message": "Login berhasil",
                    "data": data_akun,
                    "token": {
                        'refreh': refresh_token, 
                        'access': access_token
                    }
                }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Username atau kata sandi salah.'}, status=status.HTTP_400_BAD_REQUEST)
        
# AKUN

# Mendapatkan data akun berdasarkan id dan update data akun
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def akun_berdasarkan_id(request):
    try:
        id_akun = request.user.id

        # Mengambil data akun
        data = Akun.objects.get(id=id_akun)
        jumlah_kebun = Kebun.objects.filter(id_akun__id=id_akun).count()

        if request.method == "GET":
            serializer = AkunSerializer(instance=data, context={'jumlah_kebun': jumlah_kebun})

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        
        elif request.method == "PUT":
            serializer = UpdateAkunSerializer(data, data=request.data, partial=True, context={'jumlah_kebun': jumlah_kebun})
            serializer.is_valid()
            serializer.save()

            return Response({
                "message": "Data berhasil diperbarui.",
                "data": serializer.data
                }, status=status.HTTP_200_OK)
                
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Update Kata Sandi
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_kata_sandi(request):
    try:
        id_akun = request.user.id

        # Mengambil data akun
        data = Akun.objects.get(id=id_akun)

        # Mengambil data kata sandi lama dan kata sandi baru
        kata_sandi_lama = request.data.get('kata_sandi_lama')
        kata_sandi_baru = request.data.get('kata_sandi_baru')

        # Otentikasi kata sandi lama yang dimasukkan
        user = authenticate(request, username=data.username, password=kata_sandi_lama)

        if user is None:
            return Response({"detail": f"Kata sandi lama salah."}, status=status.HTTP_400_BAD_REQUEST)
        
        data.set_password(kata_sandi_baru)
        data.save()

        return Response({"message": "Kata sandi berhasil diperbarui."}, status=status.HTTP_200_OK)
                
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Update Nomor WhatsApp
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def kirim_kode_update_nomor_whatsapp(request):
    # Mengirim kode verifikasi untuk mengupdate nomor whatsapp
    try:
        id_akun = request.user.id

        # Mengambil data akun
        data = Akun.objects.get(id=id_akun)

        # Mengambil data nomor_whatsapp baru dan mengirim kode verifikasi
        nomor_whatsapp = request.data.get('nomor_whatsapp')
        
        cek = cek_numerik(nomor_whatsapp)
        if cek == False:
            return Response({"detail": "Nomor whatsapp tidak valid."}, status=status.HTTP_400_BAD_REQUEST)
    
        kode_verifikasi, waktu_kirim = kirim_kode_whatsapp(nomor_whatsapp)

        if kode_verifikasi != False:
            pass
        else:
            return Response({"detail": "Kesalahan pada pengiriman kode verifikasi"}, status=status.HTTP_409_CONFLICT)

        # Menyimpan kode verifikasi
        KodeVerifikasi.objects.create(id_akun=data, kode=kode_verifikasi, waktu_kirim=waktu_kirim, nomor_whatsapp=nomor_whatsapp)

        return Response({"message": "Kode verifikasi telah dikirimkan ke nomor whatsapp Anda."}, status=status.HTTP_200_OK)
                
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Verifikasi kode untuk update nomor whatsapp
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def verifikasi_kode_update_nomor_whatsapp(request):
    # Verifikasi kode registrasi
    kode = request.data.get("kode")

    # Memeriksa kode dari database
    kode_db = KodeVerifikasi.objects.filter(kode=kode)

    if not kode_db.exists():
        return Response({"detail": "Kode verifikasi salah."}, status=status.HTTP_400_BAD_REQUEST)

    # Mengecek apakah kode milik akun yang sesuai dan kode belum kedaluwarsa
    id_akun = request.user.id
    data = Akun.objects.get(id=id_akun)
    kode_db_data = kode_db.first()

    if kode_db_data.id_akun.id != data.id:
        return Response({"detail": "Kode verifikasi salah."}, status=status.HTTP_400_BAD_REQUEST)
    
    if timezone.now() > kode_db_data.waktu_kedaluwarsa:
        return Response({"detail": "Kode verifikasi sudah kedaluwarsa."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Jika kode ada dan belum kedaluwarsa
    # Update nomor whatsapp akun
    Akun.objects.filter(id=kode_db_data.id_akun.id).update(nomor_whatsapp=kode_db_data.nomor_whatsapp)
        
    return Response({"message": "Kode verifikasi berhasil diverifikasi."}, status=status.HTTP_200_OK)