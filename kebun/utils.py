from django.utils import timezone
from datetime import datetime
from dotenv import load_dotenv
from .models import DetailKirimNotifikasi
import tensorflow as tf
import numpy as np
import os, requests, io
import environ
from google.cloud import secretmanager

env = environ.Env(DEBUG=(bool, False))
# env_file = os.path.join(BASE_DIR, ".env")

# Pull secrets from Secret Manager
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

client = secretmanager.SecretManagerServiceClient()
settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

env.read_env(io.StringIO(payload))

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

def cek_format_tanggal(string_tanggal, format_tanggal):
    try:
        datetime.strptime(string_tanggal, format_tanggal)
        return True
    except ValueError:
        return False

# Konversi rentang tanggal dari string ke DatTimeField
def konversi_range_tanggal(tanggal_awal, tanggal_akhir):
    # Konversi tanggal ke objek datetime dengan timezone
    tanggal_awal = datetime.strptime(tanggal_awal, "%Y-%m-%d").date()
    tanggal_awal = timezone.make_aware(datetime.combine(tanggal_awal, datetime.min.time()))

    tanggal_akhir = datetime.strptime(tanggal_akhir, "%Y-%m-%d").date()
    tanggal_akhir = timezone.make_aware(datetime.combine(tanggal_akhir, datetime.max.time()))
    
    return tanggal_awal, tanggal_akhir

# Ubah nama hari dari bahasa inggris ke bahasa indonesia
def nama_hari(hari):
    if hari == 'Monday':
        hari = 'Senin'
    elif hari == 'Tuesday':
        hari = 'Selasa'
    elif hari == 'Wednesday':
        hari = 'Rabu'
    elif hari == 'Thursday':
        hari = 'Kamis'
    elif hari == 'Friday':
        hari = 'Jumat'
    elif hari == 'Saturday':
        hari = 'Sabtu'
    elif hari == 'Sunday':
        hari = 'Minggu'
    
    return hari

# Ubah nama bulan dari bahasa inggris ke bahasa indonesia
def nama_bulan(bulan):
    if bulan == 'January':
        bulan = 'Januari'
    elif bulan == 'February':
        bulan = 'Februari'
    elif bulan == 'March':
        bulan = 'Maret'
    elif bulan == 'April':
        bulan = 'April'
    elif bulan == 'May':
        bulan = 'Mei'
    elif bulan == 'June':
        bulan = 'Juni'
    elif bulan == 'July':
        bulan = 'Juli'
    elif bulan == 'August':
        bulan = 'Agustus'
    elif bulan == 'September':
        bulan = 'September'
    elif bulan == 'October':
        bulan = 'Oktober'
    elif bulan == 'November':
        bulan = 'November'
    elif bulan == 'December':
        bulan = 'Desember'

    return bulan

def membuat_pesan(parameter, keadaan):
    data = [{ "type": "text", "text": parameter }, { "type": "text", "text": keadaan }]
    return data

def mengirim_pesan_notifikasi(notifikasi, data_parameter, nomor_whatsapp):
    # Mengirim pesan notifikasi dan menambahkan data ke detail notifikasi
    url = env('WHATSAPP_URL')
    headers = { 'Authorization': 'Bearer ' + env('WHATSAPP_TOKEN') }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": nomor_whatsapp,
        "type": "template",
        "template": {
            "name": "notifikasi",
            "language": {
                "code": "id"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": data_parameter
                }
            ]
        }
    }

    response = requests.post(url, headers=headers,json=data)
    data = response.json()
    print(data)
    if "error" in data:
        pass
    else:
        DetailKirimNotifikasi.objects.create(id_notifikasi=notifikasi, pesan=data_parameter)