from rest_framework.test import APITestCase
from django.utils import timezone
from .models import Akun, KodeVerifikasi

import time

class AkunTest(APITestCase):
    def setUp(self):
        # Register data akun
        self.data_registrasi = {
            'nama_pengguna': 'testuser',
            'username': 'testusername',
            'kata_sandi': 'testpassword',
            'nomor_whatsapp': '6280000000000',
        }
        self.client.post('/api/auth/register', self.data_registrasi)
        
        # Mendapatkan kode verifikasi yang dikirim
        self.kode_verifikasi = KodeVerifikasi.objects.get(nomor_whatsapp=self.data_registrasi['nomor_whatsapp'])

        # Login akun
        data_login = {
            'username': 'testusername',
            'kata_sandi': 'testpassword'
        }
        response_login = self.client.post('/api/auth/login', data_login)
        
        # Mendapatkan token
        self.token = f"Bearer {response_login.data['token']['access']}"

        # Token tidak berlaku
        self.token_tidak_berlaku = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5Mjk2NDQwOSwiaWF0IjoxNjg1MTg4NDA5LCJqdGkiOiJlYzg4ZGZkZDQ1YWQ0OTNmYjU4MTdkNGJkNzM0MzMxOCIsInVzZXJfaWQiOjIxfQ.ZrMKLng_eSX-DpFfT7lSz6r1mzEdXUFqT3tpq61JhAA'

        # Menambahkan kdoe verifikasi untuk edit nomor whatsapp
        akun = Akun.objects.get(nomor_whatsapp=self.data_registrasi['nomor_whatsapp'])
        nomor_baru = "620000000011"
        self.kode_verifikasi_update_whatsapp = KodeVerifikasi.objects.create(id_akun=akun, kode="12345", waktu_kirim=timezone.now(), nomor_whatsapp=nomor_baru)

    def test_01_register_sukses(self):
        url = '/api/auth/register'
        
        data_akun = {
            'nama_pengguna': 'testuser',
            'username': 'testusername_1',
            'password': 'testpassword',
            'nomor_whatsapp': '6280000000001',
        }

        response = self.client.post(url, data_akun)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('data', response.data)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['message'], 'Akun berhasil didaftarkan')
        self.assertEqual(response.data['data']['username'], 'testusername_1')
    
    def test_02_register_field_sudah_digunakan(self):
        # Register gagal karena username dan nomor whatsapp sudah digunakan

        url = '/api/auth/register'
        
        data_akun = {
            'nama_pengguna': 'testuser sudah ada',
            'username': 'testusername',
            'kata_sandi': 'testpassword',
            'nomor_whatsapp': '6280000000000',
        }

        response = self.client.post(url, data_akun)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail']['username'][0], 'akun dengan username telah ada.')
        self.assertEqual(response.data['detail']['nomor_whatsapp'][0], 'akun dengan nomor whatsapp telah ada.')
    
    def test_03_register_parameter_kurang(self):
        # Field wajib seperti nomor whatsapp tidak diisi
        
        url = '/api/auth/register'

        data_akun = {
            'nama_pengguna': 'testuser sudah ada',
            'username': 'testusername',
            'password': 'testpassword',
        }
        
        response = self.client.post(url, data_akun)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail']['nomor_whatsapp'][0], 'Bidang ini harus diisi.')
    
    def test_04_verifikasi_kode_registrasi_sukses(self):
        url = '/api/verifikasi/verifikasi-kode-registrasi'

        data = {
            'kode': self.kode_verifikasi.kode
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Kode verifikasi berhasil diverifikasi.')

    def test_05_verifikasi_kode_salah(self):
        url = '/api/verifikasi/verifikasi-kode-registrasi'

        data = {
            'kode': '0000'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Kode verifikasi salah.')
    
    def test_06_verifikasi_kode_kedaluwarsa(self):
        url = '/api/verifikasi/verifikasi-kode-registrasi'

        data = {
            'kode': self.kode_verifikasi.kode
        }

        # Menjeda pengujian selama 5 menit
        time.sleep(300)

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Kode verifikasi sudah kedaluwarsa.')
    
    def test_07_verifikasi_kirim_ulang_kode_sukses(self):
        url = '/api/verifikasi/kirim-kode'

        data = {
            "nomor_whatsapp": "6280000000000"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Kode verifikasi telah dikirimkan ke nomor whatsapp Anda.')

    def test_08_verifikasi_kirim_ulang_kode_gagal(self):
        # Gagal dikarenakan nomor yang dimasukkan tidak valid

        url = '/api/verifikasi/kirim-kode'

        data = {
            "nomor_whatsapp": "62000000abcd"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Nomor whatsapp tidak valid.')

    def test_09_login_sukses(self):
        url = '/api/auth/login'

        kredensial = {
            'username': 'testusername',
            'kata_sandi': 'testpassword'
        }

        response = self.client.post(url, kredensial)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['message'], 'Login berhasil')
        self.assertEqual(response.data['data']['username'], 'testusername')
    
    def test_10_login_username_salah(self):
        # Username salah dengan yang sudah ada di database

        url = '/api/auth/login'

        kredensial = {
            'username': 'test',
            'kata_sandi': 'testpassword'
        }
        
        response = self.client.post(url, kredensial)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Username atau kata sandi salah.')
    
    def test_11_login_kata_sandi_salah(self):
        # Kata sandi salah dengan yang sudah ada di database

        url = '/api/auth/login'

        kredensial = {
            'username': 'testusername',
            'kata_sandi': 'test'
        }
        
        response = self.client.post(url, kredensial)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Username atau kata sandi salah.')
    
    def test_12_login_parameter_kurang(self):
        # Parameter kata sandi tidak diisi

        url = '/api/auth/login'

        kredensial = {
            'username': 'testusername'
        }
        
        response = self.client.post(url, kredensial)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Username dan kata sandi harus diisi')
    
    def test_13_mengambil_data_akun_sukses(self):
        url = '/api/akun'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['username'], 'testusername')
    
    def test_14_mengambil_data_akun_gagal(self):
        # Menggunakan token dari akun yang sudah tidak ada di database

        url = '/api/akun'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Pengguna tidak ditemukan')

    def test_15_update_data_akun_berhasil(self):
        url = '/api/akun'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            'nama_pengguna': 'test',
            'username': 'username'
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['nama_pengguna'], 'test')
        self.assertEqual(response.data['data']['username'], 'username')
    
    def test_16_update_data_akun_gagal(self):
        # Menggunakan token yang tidak valid

        url = '/api/akun'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        data = {
            'nama_pengguna': 'test',
            'username': 'username'
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Pengguna tidak ditemukan')
    
    def test_17_update_kata_sandi_sukse(self):
        url = '/api/akun/update-kata-sandi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "kata_sandi_lama": "testpassword",
            "kata_sandi_baru": "password"
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Kata sandi berhasil diperbarui.')

    def test_18_update_kata_sandi_gagal(self):
        # Kata sandi lama salah

        url = '/api/akun/update-kata-sandi'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "kata_sandi_lama": "test",
            "kata_sandi_baru": "password"
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Kata sandi lama salah.')

    def test_19_kirim_kode_verifikasi_update_whatsapp_sukses(self):
        url = '/api/verifikasi/kirim-kode/update-nomor-whatsapp'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "nomor_whatsapp": "620000000000"
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Kode verifikasi telah dikirimkan ke nomor whatsapp Anda.')
    
    def test_20_kirim_kode_verifikasi_update_whatsapp_nomor_tidak_valid(self):
        # Nomor whatsapp yang baru tidak valid

        url = '/api/verifikasi/kirim-kode/update-nomor-whatsapp'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "nomor_whatsapp": "62000000abcd"
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Nomor whatsapp tidak valid.')
    
    def test_21_verifikasi_kode_update_whatsapp_sukses(self):
        url = '/api/verifikasi/verifikasi-kode-nomor-whatsapp'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "kode": self.kode_verifikasi_update_whatsapp.kode
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Kode verifikasi berhasil diverifikasi.')
    
    def test_22_verifikasi_kode_update_whatsapp_kode_salah(self):
        url = '/api/verifikasi/verifikasi-kode-nomor-whatsapp'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "kode": "0000"
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Kode verifikasi salah.')
    
    def test_23_verifikasi_kode_update_whatsapp_kode_kedaluwarsa(self):
        url = '/api/verifikasi/verifikasi-kode-nomor-whatsapp'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "kode": self.kode_verifikasi_update_whatsapp.kode
        }

        # Menjeda pengujian selama 5 menit
        time.sleep(300)

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Kode verifikasi sudah kedaluwarsa.')