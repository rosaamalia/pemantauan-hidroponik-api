from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Avg
from django.utils import timezone
from django.utils.dateparse import parse_date
from base.utils import paginated_queryset, verifikasi_id_akun
from kebun.models import Kebun
from .models import DataKebun
from .serializers import DataKebunSerializer
from .utils import konversi_range_tanggal
from datetime import date, timedelta

# Create your views here.
def index(request):
    return render(request, "index.html")

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def data_kebun_berdasarkan_id_kebun(request):
    try:
        id_akun = request.user.id

        if request.method == "GET":
            # Mendapatkan semua data kebun berdasarkan id_kebun

            id_kebun = request.GET.get('id_kebun')
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
            serializer = DataKebunSerializer(instance=result_page, many=True)

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

            id_kebun = data['id_kebun']
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

def ambil_data_rata_rata(tanggal, id_kebun):
    tanggal_awal, tanggal_akhir = konversi_range_tanggal(tanggal, tanggal)
    data_filter = DataKebun.objects.filter(id_kebun__id=id_kebun, created_at__range=(tanggal_awal, tanggal_akhir))

    # Ambil data untuk setiap parameter
    ph = data_filter.aggregate(avg_value=Avg('ph'))
    temperatur = data_filter.aggregate(avg_value=Avg('temperatur'))
    tds = data_filter.aggregate(avg_value=Avg('tds'))
    intensitas_cahaya = data_filter.aggregate(avg_value=Avg('intensitas_cahaya'))
    kelembapan = data_filter.aggregate(avg_value=Avg('kelembapan'))

    # Menggabungkan rata-rata parameter
    data = {
        'tanggal': tanggal,
        'ph': ph['avg_value'],
        'temperatur': temperatur['avg_value'],
        'tds': tds['avg_value'],
        'intensitas_cahaya': intensitas_cahaya['avg_value'],
        'kelembapan': kelembapan['avg_value'],
    }

    return data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def data_kebun_rata_rata(request):
    # Mengambil rata-rata data kebun setiap parameter dalam seminggu
    
    id_kebun = request.GET.get('id_kebun')

    today = date.today()
    data = []

    for i in range(0, 7):
        tanggal = str(today - timedelta(days=i))
        data.append(ambil_data_rata_rata(tanggal, id_kebun))

    return Response({
        "message": "Data berhasil diambil.",
        "data": data
        }, status=status.HTTP_200_OK)