from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .models import JenisTanaman
from .serializers import JenisTanamanSerializer
from base.utils import paginated_queryset

import tensorflow as tf
import numpy as np

@api_view(['GET'])
@permission_classes([AllowAny])
def get_jenis_tanaman(request):
    data = JenisTanaman.objects.all().order_by('nama_tanaman')
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

def classify_data(input_details, interpreter, data):
  # run inference
  interpreter.set_tensor(input_details[0]['index'], data)
  interpreter.invoke()

  output_details = interpreter.get_output_details()[0]['index']
  output = interpreter.get_tensor(output_details)

  return output

@api_view(['GET'])
@permission_classes([AllowAny])
def prediction(request):
    tds = 0.490833
    light_intensity = 0.861667
    pH = 0.364933

    tflite_model_file = 'jenis_tanaman/models/tomat/model.tflite'

    with open(tflite_model_file, 'rb') as fid:
        tflite_model = fid.read()

    interpreter = tf.lite.Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()

    input_data = np.array([[tds, light_intensity, pH]])
    input_data = input_data.astype('float32')

    prediction = classify_data(input_details, interpreter, input_data)

    # Menyusun respons JSON dengan hasil prediksi
    response_data = {
        'pH': pH,
        'TDS': tds,
        'Light Intensity': light_intensity,
        'prediction': np.argmax(prediction)
    }

    return Response({"data": response_data}, status=status.HTTP_200_OK)