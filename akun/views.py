from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import AkunSerializer

# Register
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data.copy()
    data["terverifikasi"] = True
    data["password"] = request.data["kata_sandi"]
    del data["kata_sandi"]

    serializer = AkunSerializer(data=data)

    if serializer.is_valid():
            hashed_password = make_password(data['password'])

            # Menyimpan data dan generate token untuk akun baru
            serializer.validated_data['password'] = hashed_password
            akun = serializer.save()
            refresh = RefreshToken.for_user(akun)

            return Response({
                "message": "Akun berhasil didaftarkan",
                "data": serializer.data,
                "token" : {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)
    
    return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
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
            return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Request dengan basic authentication
        username = request.data.get('username')
        password = request.data.get('kata_sandi')

        if not username or not password:
            return Response({'message': 'Username dan kata sandi harus diisi'}, status=status.HTTP_400_BAD_REQUEST)
    
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
            return Response({'message': 'Username atau kata sandi salah.'}, status=status.HTTP_400_BAD_REQUEST)