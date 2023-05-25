from datetime import datetime

import tensorflow as tf
import numpy as np

def classify_data(input_details, interpreter, data):
  # run inference
  interpreter.set_tensor(input_details[0]['index'], data)
  interpreter.invoke()

  output_details = interpreter.get_output_details()[0]['index']
  output = interpreter.get_tensor(output_details)

  return output

# Fungsi untuk menjalankan model klasifikasi
def prediction(tds, intensitas_cahaya, ph, tflite_model_file):
    with open(tflite_model_file, 'rb') as fid:
        tflite_model = fid.read()

    interpreter = tf.lite.Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()

    input_data = np.array([[tds, intensitas_cahaya, ph]])
    input_data = input_data.astype('float32')

    output = classify_data(input_details, interpreter, input_data)

    return np.argmax(output)

# Konversi rentang tanggal dari string ke DatTimeField
def konversi_range_tanggal(tanggal_awal, tanggal_akhir):
    detail_tanggal_awal = tanggal_awal.split('-')
    tanggal_awal = datetime(int(detail_tanggal_awal[0]), int(detail_tanggal_awal[1]), int(detail_tanggal_awal[2]), 0, 0, 0)

    detail_tanggal_akhir = tanggal_akhir.split('-')
    tanggal_akhir = datetime(int(detail_tanggal_akhir[0]), int(detail_tanggal_akhir[1]), int(detail_tanggal_akhir[2]), 23, 59, 59)
    
    return tanggal_awal, tanggal_akhir