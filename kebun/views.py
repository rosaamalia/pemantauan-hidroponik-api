from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Avg
from base.utils import paginated_queryset, verifikasi_id_akun
from .models import Kebun, DataKebun
from .serializers import SemuaKebunSerializer, KebunSerializer, DataKebunSerializer, GetDataKebunSerializer
from .utils import konversi_range_tanggal
from datetime import date, timedelta

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def kebun(request):
    try:
        id_akun = request.user.id

        # Mengambil semua data kebun berdasarkan id akun
        if request.method == "GET":
            kebun = Kebun.objects.filter(id_akun=id_akun).order_by("-created_at")
            paginator, result_page = paginated_queryset(kebun, request)
            serializer = SemuaKebunSerializer(instance=result_page, many=True)

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
                
    except ObjectDoesNotExist:
        return Response({"detail": f"Data kebun untuk akun dengan id {id_akun} tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def kebun_berdasarkan_id(request, id_kebun):
    try:
        id_akun = request.user.id
        kebun = Kebun.objects.filter(id_akun__id=id_akun).get(id=id_kebun)

        # Mendapatkan data berdasarkan id kebun
        if request.method == "GET":
            serializer = SemuaKebunSerializer(instance=kebun)

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        
        # Meng-update data kebun berdasarkan id kebun
        elif request.method == "PUT":
            serializer = KebunSerializer(kebun, data=request.data, partial=True)

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
            kebun.delete()
            return Response({"message": "Data berhasil dihapus." }, status=status.HTTP_200_OK)
                
    except ObjectDoesNotExist:
        return Response({"detail": f"Data kebun dengan id {id_kebun} untuk akun {id_akun} tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def cari_kebun(request):
    # Mengambil data kebun sesuai dengan keyword pencarian

    id_akun = request.user.id
    q = request.GET.get('q')

    data = Kebun.objects.filter(
        Q(nama_kebun__icontains=q) |
        Q(deskripsi__icontains=q) |
        Q(id_jenis_tanaman__nama_tanaman__icontains=q) |
        Q(alamat__icontains=q)
    ).filter(id_akun__id=id_akun).order_by('-created_at')

    paginator, result_page = paginated_queryset(data, request)
    serializer = SemuaKebunSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)

# Data Kebun

# Create your views here.
def index(request):
    return render(request, "index.html")

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def data_kebun_berdasarkan_id_kebun(request, id_kebun):
    try:
        id_akun = request.user.id

        if request.method == "GET":
            # Mendapatkan semua data kebun berdasarkan id_kebun

            kebun = Kebun.objects.get(id=id_kebun)

            verifikasi_id_akun(id_akun, kebun.id_akun.id) # Verifikasi pemilik kebun

            # Mengambil data rentang tanggal jika ada
            tanggal_awal = request.GET.get("tanggal_awal")
            tanggal_akhir = request.GET.get("tanggal_akhir")

            if tanggal_awal != None and tanggal_akhir != None:
                # Konversi tanggal dalam bentuk DateTimeFiedl
                tanggal_awal, tanggal_akhir = konversi_range_tanggal(tanggal_awal, tanggal_akhir)
                data_kebun = DataKebun.objects.filter(id_kebun__id=id_kebun, created_at__range=(tanggal_awal, tanggal_akhir)).order_by("-created_at")
            else:
                data_kebun = DataKebun.objects.filter(id_kebun__id=id_kebun).order_by("-created_at")
            
            paginator, result_page = paginated_queryset(data_kebun, request)
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
            kebun = Kebun.objects.get(id=id_kebun)
            verifikasi_id_akun(id_akun, kebun.id_akun.id) # Verifikasi pemilik kebun

            serializer = DataKebunSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data berhasil ditambahkan",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
    except ObjectDoesNotExist:
        return Response({"detail": f"Data kebun untuk akun dengan id {id_akun} tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

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