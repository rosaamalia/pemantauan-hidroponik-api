from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q, Avg
from base.utils import paginated_queryset, verifikasi_id_akun
from kebun_disematkan.models import KebunDisematkan
from .models import Kebun, DataKebun, Notifikasi
from .serializers import SemuaKebunSerializer, KebunSerializer, DataKebunSerializer, GetDataKebunSerializer, NotifikasiSerializer
from .utils import konversi_range_tanggal, cek_format_tanggal
from datetime import date, timedelta

# Kebun

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def kebun(request):
    try:
        id_akun = request.user.id

        # Mengambil semua data kebun berdasarkan id akun
        if request.method == "GET":
            page = request.GET.get('page')
            kebun = Kebun.objects.filter(id_akun=id_akun).order_by("-created_at")

            if (page is None):
                serializer = SemuaKebunSerializer(kebun, many=True, context={'request': request})
                return Response({
                    "message": "Data berhasil diambil",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
            else:
                paginator, result_page = paginated_queryset(kebun, request)
                serializer = SemuaKebunSerializer(instance=result_page, many=True, context={'request': request})

                return paginator.get_paginated_response(serializer.data)
        
        # Menambahkan data kebun baru sesuai dengan id akun
        elif request.method == "POST":
            data = request.data.copy()
            data["id_akun"] = id_akun
            serializer = KebunSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data berhasil ditambahkan",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def kebun_berdasarkan_id(request, id_kebun):
    try:
        id_akun = request.user.id
        kebun = Kebun.objects.get(id=id_kebun)

        verifikasi_id_akun(id_akun, kebun.id_akun.id) # Verifikasi pemilik kebun

        # Mendapatkan data berdasarkan id kebun
        if request.method == "GET":
            serializer = SemuaKebunSerializer(instance=kebun, context={'request': request})

            return Response({
                "message": "Data berhasil diambil.",
                "data": serializer.data
                }, status=status.HTTP_200_OK)
        
        # Meng-update data kebun berdasarkan id kebun
        elif request.method == "PUT":
            serializer = SemuaKebunSerializer(kebun, data=request.data, partial=True, context={'request': request})

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data berhasil diperbarui.",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Menghapus data kebun berdasarkan id kebun
        elif request.method == "DELETE":
            kebun_disematkan = KebunDisematkan.objects.get(id_akun=id_akun)
            kebun_disematkan.kebun.remove(id_kebun)
            kebun_disematkan.save()

            kebun.delete()
            return Response({"message": "Data berhasil dihapus." }, status=status.HTTP_200_OK)
                
    except Exception as e:
        if isinstance(e, ObjectDoesNotExist):
            return Response({"detail": "Data kebun tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(e, PermissionDenied):
            return Response({"detail": "Pengguna tidak diperbolehkan untuk mengakses data."}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def cari_kebun(request):
    # Mengambil data kebun sesuai dengan keyword pencarian

    id_akun = request.user.id
    q = request.GET.get('q')

    if q is None:
        return Response({"detail": "Paramater 'q' harus diisi."}, status=status.HTTP_400_BAD_REQUEST)

    data = Kebun.objects.filter(
        Q(nama_kebun__icontains=q) |
        Q(deskripsi__icontains=q) |
        Q(id_jenis_tanaman__nama_tanaman__icontains=q) |
        Q(alamat__icontains=q)
    ).filter(id_akun__id=id_akun).order_by('-created_at')

    paginator, result_page = paginated_queryset(data, request)
    serializer = SemuaKebunSerializer(result_page, many=True, context={'request': request})

    return paginator.get_paginated_response(serializer.data)

# Data Kebun

def index(request):
    return render(request, "index.html")

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def data_kebun_berdasarkan_id_kebun(request, id_kebun):
    try:
        id_akun = request.user.id

        kebun = Kebun.objects.get(id=id_kebun)
        verifikasi_id_akun(id_akun, kebun.id_akun.id) # Verifikasi pemilik kebun

        if request.method == "GET":
            # Mendapatkan semua data kebun berdasarkan id_kebun


            # Mengambil data rentang tanggal jika ada
            tanggal_awal = request.GET.get("tanggal_awal")
            tanggal_akhir = request.GET.get("tanggal_akhir")

            if tanggal_awal != None and tanggal_akhir != None:
                format_tanggal_awal = cek_format_tanggal(tanggal_awal, "%Y-%m-%d")
                format_tanggal_akhir = cek_format_tanggal(tanggal_akhir, "%Y-%m-%d")

                if format_tanggal_awal == False or format_tanggal_akhir == False:
                    return Response({"detail": "Tanggal tidak valid. Tanggal harus dalam format '%Y-%m-%d'."}, status=status.HTTP_400_BAD_REQUEST)

                # Konversi tanggal dalam bentuk DateTimeFiedl
                tanggal_awal, tanggal_akhir = konversi_range_tanggal(tanggal_awal, tanggal_akhir)
                data_kebun = DataKebun.objects.filter(id_kebun__id=id_kebun, created_at__range=(tanggal_awal, tanggal_akhir)).order_by("-created_at")
            else:
                data_kebun = DataKebun.objects.filter(id_kebun__id=id_kebun).order_by("-created_at")
            
            paginator, result_page = paginated_queryset(data_kebun, request, 15)
            serializer = GetDataKebunSerializer(instance=result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        
        elif request.method == "POST":
            # param_query = request.GET
            # data = {
            #     'id_kebun': param_query.get('id_kebun'),
            #     'ph': param_query.get('ph'),
            #     'temperatur': param_query.get('temperatur'),
            #     'tds': param_query.get('tds'),
            #     'intensitas_cahaya': param_query.get('intensitas_cahaya'),
            #     'kelembapan': param_query.get('kelembapan')
            # }
            data = request.data.copy()
            data['id_kebun'] = id_kebun

            serializer = DataKebunSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data berhasil ditambahkan",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        if isinstance(e, ObjectDoesNotExist):
            return Response({"detail": "Data kebun tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(e, PermissionDenied):
            return Response({"detail": "Pengguna tidak diperbolehkan untuk mengakses data."}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def ambil_data_rata_rata(id_kebun, parameter):
    today = date.today()
    data = {}

    for i in range(0, 7):
        tanggal = str(today - timedelta(days=i))
        tanggal_awal, tanggal_akhir = konversi_range_tanggal(tanggal, tanggal)
        data_filter = DataKebun.objects.filter(id_kebun__id=id_kebun, created_at__range=(tanggal_awal, tanggal_akhir))
        
        # Ambil data untuk parameter
        data_parameter = data_filter.aggregate(avg_value=Avg(parameter))
        data[tanggal] = data_parameter['avg_value']

    return {str(parameter): data}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def data_kebun_rata_rata(request, id_kebun):
    try:
        id_akun = request.user.id
        kebun = Kebun.objects.get(id=id_kebun)
        verifikasi_id_akun(id_akun, kebun.id_akun.id) # Verifikasi pemilik kebun

        # Mengambil rata-rata data kebun setiap parameter dalam seminggu
        parameter = ['ph', 'temperatur', 'tds', 'intensitas_cahaya', 'kelembapan']
        data = []

        for i in parameter:
            data_parameter = ambil_data_rata_rata(id_kebun, i)
            data.append(data_parameter)

        return Response({
            "message": "Data berhasil diambil.",
            "data": data
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        if isinstance(e, ObjectDoesNotExist):
            return Response({"detail": "Data kebun tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(e, PermissionDenied):
            return Response({"detail": "Pengguna tidak diperbolehkan untuk mengakses data."}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Notifikasi

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def notifikasi(request, id_kebun):
    try:
        id_akun = request.user.id
        notifikasi = Notifikasi.objects.get(id_kebun=id_kebun)
        verifikasi_id_akun(id_akun, notifikasi.id_kebun.id_akun.id) # Verifikasi pemilik kebun

        # Mendapatkan data notifikasi berdasarkan id kebun
        if request.method == "GET":
            serializer = NotifikasiSerializer(instance=notifikasi)

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        
        # Meng-update data notifikasi berdasarkan id kebun
        elif request.method == "PUT":
            serializer = NotifikasiSerializer(notifikasi, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data berhasil diperbarui.",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        if isinstance(e, ObjectDoesNotExist):
            return Response({"detail": "Data kebun tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(e, PermissionDenied):
            return Response({"detail": "Pengguna tidak diperbolehkan untuk mengakses data."}, status=status.HTTP_401_UNAUTHORIZED)
        

        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)