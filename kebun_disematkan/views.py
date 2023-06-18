from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import KebunDisematkan
from .serializers import KebunDisematkanSerializer, SemuaKebunDisematkanSerializer

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def kebun_disematkan(request):
    try:
        id_akun = request.user.id
        kebun_disematkan = KebunDisematkan.objects.filter(id_akun=id_akun).first()

        # Mengambil semua data kebun disematkan berdasarkan id akun
        if request.method == "GET":
            serializer = KebunDisematkanSerializer(instance=kebun_disematkan)

            return Response({
                    "message": "Data berhasil diambil.",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
        
        # Meg-update daftar kebun disematkan sesuai dengan id akun
        elif request.method == "PUT":
            serializer = KebunDisematkanSerializer(kebun_disematkan, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data berhasil diperbarui.",
                    "data": serializer.data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)