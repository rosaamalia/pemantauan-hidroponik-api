from django.utils import timezone
import os, requests, random, re, io
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

def cek_numerik(input_string):
    pattern = r'^\d+$'  # Hanya karakter angka dari awal hingga akhir string
    match = re.match(pattern, input_string)
    return bool(match)

def generate_kode():
    # Membuat string kode verifikasi yang terdiri dari 5 angka
    number_string = ''.join(random.choices('0123456789', k=5))
    return number_string

def kirim_kode_whatsapp(nomor_whatsapp):
    # Mengirim kode verifikasi menggunakan pesan whatsapp
    # Jika kode berhasil dikirim, akan mengembalikan kode verifikasi dan waktu pengiriman

    kode = generate_kode()
    url = env('WHATSAPP_URL')
    headers = { 'Authorization': 'Bearer ' + env('WHATSAPP_TOKEN') }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": nomor_whatsapp,
        "type": "template",
        "template": {
            "name": "kode_verifikasi",
            "language": {
                "code": "id"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": kode
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": kode
                        }
                    ]
                }
            ]
        }
    }
    
    response = requests.post(url, headers=headers,json=data)
    data = response.json()

    if "error" in data:
        return False, None
    else:
        return kode, timezone.now()