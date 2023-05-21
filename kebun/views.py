from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from base.utils import paginated_queryset
from .models import Kebun
from .serializers import SemuaKebunSerializer, KebunSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def kebun(request):
    try:
        id_akun = request.user.id

        if request.method == "GET":
            kebun = Kebun.objects.filter(id_akun=id_akun).order_by("-created_at")
            paginator, result_page = paginated_queryset(kebun, request)
            serializer = SemuaKebunSerializer(instance=result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        
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

        if request.method == "GET":
            serializer = SemuaKebunSerializer(instance=kebun)

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        
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
        
        elif request.method == "DELETE":
            kebun.delete()
            return Response({"message": "Data berhasil dihapus." }, status=status.HTTP_200_OK)
                
    except ObjectDoesNotExist:
        return Response({"detail": f"Data kebun dengan id {id_kebun} untuk akun {id_akun} tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def cari_kebun(request):
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