from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from base.utils import paginated_queryset
from kebun.models import Kebun
from .models import DataKebun
from .serializers import DataKebunSerializer

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
            pass
            # kebun = Kebun.objects.filter(id_akun=id_akun).order_by("-created_at")
            # paginator, result_page = paginated_queryset(kebun, request)
            # serializer = SemuaKebunSerializer(instance=result_page, many=True)

            # return paginator.get_paginated_response(serializer.data)
        
        elif request.method == "POST":
            param_query = request.GET
            data = {
                'id_kebun': param_query.get('id_kebun'),
                'ph': param_query.get('ph'),
                'temperatur': param_query.get('temperatur'),
                'tds': param_query.get('tds'),
                'intensitas_cahaya': param_query.get('intensitas_cahaya'),
                'kelembapan': param_query.get('kelembapan'),
                'ec': param_query.get('ec')
            }

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