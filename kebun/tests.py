from rest_framework.test import APITestCase
from django.core.exceptions import ObjectDoesNotExist
from akun.models import Akun
from .models import Kebun, DataKebun, JenisTanaman, Notifikasi

import random
from datetime import datetime, timedelta

def random_id_kebun(kebun_queryset):
    existing_ids = kebun_queryset.values_list('id', flat=True)  # Mengambil daftar id kebun yang sudah ada
    all_ids = range(1, max(existing_ids)+2)  # Membuat daftar semua angka mulai dari 1 hingga id maksimum + 1

    available_ids = list(set(all_ids) - set(existing_ids))  # Menghitung perbedaan antara semua id dan id yang sudah ada
    random_id = random.choice(available_ids)  # Mengambil id acak dari daftar id yang tersedia

    return random_id

class KebunTest(APITestCase):
    def setUp(self):
        self.akun = Akun.objects.create_user(nama_pengguna='testuser', username='testusername', password='testpassword', nomor_whatsapp='6280000000000')

        # Login akun
        data_login = {
            'username': 'testusername',
            'kata_sandi': 'testpassword'
        }
        response_login = self.client.post('/api/auth/login', data_login)
        
        # Mendapatkan token
        self.token = f"Bearer {response_login.data['token']['access']}"

        # Token tidak berlaku
        self.token_tidak_berlaku = 'Bearer TOKEN_TIDAK_VALID'

        self.jenis_tanaman = JenisTanaman.objects.create(id=1, nama_tanaman='Tomat', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='jenis_tanaman/models/tomat/model.tflite')

        kebun = [
            Kebun(id_akun=self.akun, id_jenis_tanaman=self.jenis_tanaman, nama_kebun='Kebun Tomat 1', deskripsi='Deskripsi'),
            Kebun(id_akun=self.akun, id_jenis_tanaman=self.jenis_tanaman, nama_kebun='Kebun Tomat 2', deskripsi='Deskripsi'),
            Kebun(id_akun=self.akun, id_jenis_tanaman=self.jenis_tanaman, nama_kebun='Kebun Tomat 3', deskripsi='Deskripsi'),
        ]
        Kebun.objects.bulk_create(kebun)

        # Membuat notifikasi untuk salah satu kebun
        self.kebun = Kebun.objects.filter(id_akun__id=self.akun.id).first()
        Notifikasi.objects.create(id_kebun=self.kebun)

        # Menambahkan data parameter kebun
        data_kebun = [
            DataKebun(id_kebun=self.kebun, ph=5.709, temperatur=32, tds=73, intensitas_cahaya=1289, kelembapan=576),
            DataKebun(id_kebun=self.kebun, ph=5.709, temperatur=32, tds=73, intensitas_cahaya=1289, kelembapan=576),
            DataKebun(id_kebun=self.kebun, ph=5.709, temperatur=32, tds=73, intensitas_cahaya=1289, kelembapan=576),
            DataKebun(id_kebun=self.kebun, ph=5.709, temperatur=32, tds=73, intensitas_cahaya=1289, kelembapan=576),
        ]
        DataKebun.objects.bulk_create(data_kebun)

        # Kebun lain milik pengguna lain
        akun_baru = Akun.objects.create_user(nama_pengguna='test', username='username', password='testpassword', nomor_whatsapp='6280000000002')
        self.kebun_pengguna_lain = Kebun.objects.create(id_akun=akun_baru, id_jenis_tanaman=self.jenis_tanaman, nama_kebun='Kebun Tomat 4', deskripsi='Deskripsi')

        # Random id selain yang ada di database
        daftar_kebun = Kebun.objects.filter(id_akun__id=self.akun.id)
        self.random_id = random_id_kebun(daftar_kebun)

    """ Model Kebun """

    def test_01_mendapatkan_data_kebun_pengguna_sukses(self):
        url = '/api/kebun/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 3)
    
    def test_02_mendapatkan_data_kebun_pengguna_gagal(self):
        url = '/api/kebun/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_03_menambahkan_data_kebun_pengguna_sukses(self):
        url = '/api/kebun/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "id_jenis_tanaman": 1,
            "nama_kebun": "Kebun Indah",
            "deskripsi": "Deskripsi"
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['message'], 'Data berhasil ditambahkan')
    
    def test_04_menambahkan_data_kebun_pengguna_token_invalid(self):
        url = '/api/kebun/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        data = {
            "id_jenis_tanaman": 1,
            "nama_kebun": "Kebun Indah",
            "deskripsi": "Deskripsi"
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_05_menambahkan_data_kebun_pengguna_parameter_kurang(self):
        url = '/api/kebun/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "nama_kebun": "Kebun Indah"
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail']['id_jenis_tanaman'][0], 'Bidang ini harus diisi.')
        self.assertEqual(response.data['detail']['deskripsi'][0], 'Bidang ini harus diisi.')
    
    def test_06_mencari_kebun_dengan_keyword_sukses(self):
        keyword = 'tomat'
        url = f'/api/kebun/cari?q={keyword}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 3)
        for result in response.data['results']:
            self.assertEqual(result['id_akun'], self.akun.id)
    
    def test_07_mencari_kebun_dengan_keyword_tidak_ditemukan(self):
        keyword = 'selada'
        url = f'/api/kebun/cari?q={keyword}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
    
    def test_08_mencari_kebun_dengan_keyword_gagal(self):
        url = f'/api/kebun/cari'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], "Paramater 'q' harus diisi.")
    
    def test_09_mendapatkan_data_kebun_berdasarkan_id_sukses(self):
        url = f'/api/kebun/{self.kebun.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['message'], 'Data berhasil diambil.')
        self.assertEqual(response.data['data']['id'], self.kebun.id)
    
    def test_10_mendapatkan_data_kebun_berdasarkan_id_selain_milik_pengguna(self):
        # Mengambil data dengan id kebun bukan milik pengguna
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')
    
    def test_11_mendapatkan_data_kebun_berdasarkan_id_token_invalid(self):
        url = f'/api/kebun/{self.kebun.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_12_mendapatkan_data_kebun_berdasarkan_id_tidak_valid(self):
        # Id kebun tidak ada di database
        url = f'/api/kebun/{self.random_id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')
    
    def test_13_mengupdate_data_kebun_sukses(self):
        url = f'/api/kebun/{self.kebun.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "nama_kebun": "Kebun Tomat Segar"
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['message'], 'Data berhasil diperbarui.')
        self.assertEqual(response.data['data']['id'], self.kebun.id)
        self.assertEqual(response.data['data']['nama_kebun'], 'Kebun Tomat Segar')
    
    def test_14_mengupdate_data_kebun_selain_milik_pengguna(self):
        # Mengambil data dengan id kebun bukan milik pengguna
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "nama_kebun": "Kebun Tomat Segar"
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')
    
    def test_15_mengupdate_data_kebun_token_invalid(self):
        url = f'/api/kebun/{self.kebun.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        data = {
            "nama_kebun": "Kebun Tomat Segar"
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')

    def test_16_mengupdate_data_kebun_id_tidak_valid(self):
        # Id kebun tidak ada di database
        url = f'/api/kebun/{self.random_id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "nama_kebun": "Kebun Tomat Segar"
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')
    
    def test_17_menghapus_data_kebun_sukses(self):
        url = f'/api/kebun/{self.kebun.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Data berhasil dihapus.')

        try:
            Kebun.objects.get(id=self.kebun.id)
        except Exception as e:
            self.assertEqual(isinstance(e, ObjectDoesNotExist), True)
    
    def test_18_menghapus_data_kebun_selain_milik_pengguna(self):
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')
    
    def test_19_menghapus_data_kebun_token_invalid(self):
        url = f'/api/kebun/{self.kebun.id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')

    def test_20_menghapus_data_kebun_id_tidak_valid(self):
        # Id kebun tidak ada di database
        url = f'/api/kebun/{self.random_id}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')

    """ Model Data Kebun """

    def test_21_tambah_data_kebun_sukses(self):
        url = f'/api/kebun/{self.kebun.id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "ph": 5.709,
            "temperatur": 32,
            "kelembapan": 73,
            "tds": 1289,
            "intensitas_cahaya": 578
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['message'], 'Data berhasil ditambahkan')
        self.assertEqual(response.data['data']['id_kebun'], self.kebun.id)
    
    def test_22_tambah_data_kebun_selain_milik_pengguna(self):
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "ph": 5.709,
            "temperatur": 32,
            "kelembapan": 73,
            "tds": 1289,
            "intensitas_cahaya": 578
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')
    
    def test_23_tambah_data_kebun_token_invalid(self):
        url = f'/api/kebun/{self.kebun.id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        data = {
            "ph": 5.709,
            "temperatur": 32,
            "kelembapan": 73,
            "tds": 1289,
            "intensitas_cahaya": 578
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_24_tambah_data_kebun_id_tidak_valid(self):
        url = f'/api/kebun/{self.random_id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "ph": 5.709,
            "temperatur": 32,
            "kelembapan": 73,
            "tds": 1289,
            "intensitas_cahaya": 578
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')
    
    def test_25_tambah_data_kebun_parameter_kurang(self):
        url = f'/api/kebun/{self.kebun.id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "ph": 5.709,
            "temperatur": 32,
            "kelembapan": 73
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail']['tds'][0], 'Bidang ini harus diisi.')
        self.assertEqual(response.data['detail']['intensitas_cahaya'][0], 'Bidang ini harus diisi.')
    
    def test_26_mengambil_data_kebun_berdasarkan_id_kebun_sukses(self):
        url = f'/api/kebun/{self.kebun.id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 4)
        for result in response.data['results']:
            self.assertEqual(result['id_kebun'], self.kebun.id)
    
    def test_27_mengambil_data_kebun_berdasarkan_id_kebun_selain_milik_pengguna(self):
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')

    def test_28_mengambil_data_kebun_berdasarkan_id_kebun_token_invalid(self):
        url = f'/api/kebun/{self.kebun.id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_29_mengambil_data_kebun_berdasarkan_id_tidak_valid(self):
        url = f'/api/kebun/{self.random_id}/data'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')
    
    def test_30_mengambil_data_kebun_dengan_rentang_waktu_sukses(self):
        tanggal_awal = datetime.now().strftime("%Y-%m-%d")
        tanggal_akhir = datetime.now().date() + timedelta(days=2)
        url = f'/api/kebun/{self.kebun.id}/data?tanggal_awal={tanggal_awal}&tanggal_akhir={tanggal_akhir}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 4)
        for result in response.data['results']:
            self.assertEqual(result['id_kebun'], self.kebun.id)
    
    def test_31_mengambil_data_kebun_dengan_rentang_waktu_gagal(self):
        tanggal_awal = datetime.now().strftime("%d-%m-%Y")
        tanggal_akhir = datetime.now().date() + timedelta(days=2)
        url = f'/api/kebun/{self.kebun.id}/data?tanggal_awal={tanggal_awal}&tanggal_akhir={tanggal_akhir}'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], "Tanggal tidak valid. Tanggal harus dalam format '%Y-%m-%d'.")
    
    def test_32_mengambil_rata_rata_data_kebun_sukses(self):
        hari_ini = datetime.now().strftime("%Y-%m-%d")
        url = f'/api/kebun/{self.kebun.id}/data/rata-rata'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertIn(hari_ini, response.data['data'][0]['ph'])
    
    def test_33_mengambil_rata_rata_data_kebun_selain_milik_pengguna(self):
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}/data/rata-rata'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')
    
    def test_34_mengambil_rata_rata_data_kebun_token_invalid(self):
        url = f'/api/kebun/{self.kebun.id}/data/rata-rata'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_35_mengambil_rata_rata_data_kebun_id_tidak_valid(self):
        url = f'/api/kebun/{self.random_id}/data/rata-rata'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')
    
    """ Model Notifikasi """

    def test_36_mengambil_data_notifikasi_kebun_sukses(self):
        url = f'/api/kebun/{self.kebun.id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['id_kebun'], self.kebun.id)

    def test_37_mengambil_data_notifikasi_kebun_selain_milik_pengguna(self):
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')
    
    def test_38_mengambil_data_notifikasi_kebun_token_invalid(self):
        url = f'/api/kebun/{self.kebun.id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_39_mengambil_data_notifikasi_kebun_id_tidak_valid(self):
        url = f'/api/kebun/{self.random_id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')
    
    def test_40_update_data_notifikasi_kebun_sukses(self):
        url = f'/api/kebun/{self.kebun.id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "intensitas_cahaya_min": 500,
            "intensitas_cahaya_max": 600,
            "kelembapan_min": 70,
            "kelembapan_max": 100
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['id_kebun'], self.kebun.id)
    
    def test_41_update_data_notifikasi_kebun_selain_milik_pengguna(self):
        url = f'/api/kebun/{self.kebun_pengguna_lain.id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "intensitas_cahaya_min": 500,
            "intensitas_cahaya_max": 600,
            "kelembapan_min": 70,
            "kelembapan_max": 100
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Pengguna tidak diperbolehkan untuk mengakses data.')
    
    def test_42_update_data_notifikasi_kebun_invalid_token(self):
        url = f'/api/kebun/{self.kebun.id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        data = {
            "intensitas_cahaya_min": 500,
            "intensitas_cahaya_max": 600,
            "kelembapan_min": 70,
            "kelembapan_max": 100
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_43_update_data_notifikasi_kebun_id_tidak_valid(self):
        url = f'/api/kebun/{self.random_id}/notifikasi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "intensitas_cahaya_min": 500,
            "intensitas_cahaya_max": 600,
            "kelembapan_min": 70,
            "kelembapan_max": 100
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Data kebun tidak ditemukan.')