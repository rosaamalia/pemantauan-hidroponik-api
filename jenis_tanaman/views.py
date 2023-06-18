from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .models import JenisTanaman
from .serializers import JenisTanamanSerializer
from base.utils import paginated_queryset

@api_view(['GET'])
@permission_classes([AllowAny])
def get_jenis_tanaman(request):
    page = request.GET.get('page')
    data = JenisTanaman.objects.all().order_by('nama_tanaman')

    if (page is None):
        serializer = JenisTanamanSerializer(data, many=True)
        return Response({
                "message": "Data berhasil diambil.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
    else:
        paginator, result_page = paginated_queryset(data, request)
        serializer = JenisTanamanSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def jenis_tanaman_berdasarkan_id(request, id_jenis_tanaman):
    try:
        data = JenisTanaman.objects.get(id=id_jenis_tanaman)
        serializer = JenisTanamanSerializer(instance=data)

        return Response({
                "message": "Data berhasil diambil.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({"detail": f"Data jenis tanaman dengan id {id_jenis_tanaman} tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def cari_jenis_tanaman(request):
    q = request.GET.get('q')

    data = JenisTanaman.objects.filter(
        Q(nama_tanaman__icontains=q) |
        Q(deskripsi__icontains=q) |
        Q(teks_artikel__icontains=q)
    ).order_by('id')

    paginator, result_page = paginated_queryset(data, request)
    serializer = JenisTanamanSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)