from rest_framework.test import APITestCase
from .models import Akun, KodeVerifikasi

import time

class AkunTest(APITestCase):
    def setUp(self):
        data_registrasi = {
            'nama_pengguna': 'testuser',
            'username': 'testusername',
            'kata_sandi': 'testpassword',
            'nomor_whatsapp': '6280000000000',
        }

        response_registrasi = self.client.post('/api/auth/register', data_registrasi)
        # Mendapatkan kode verifikasi yang dikirim
        self.kode_verifikasi = KodeVerifikasi.objects.get(id_akun__id=response_registrasi.data['data']['id'])

        data_login = {
            'username': 'testusername',
            'kata_sandi': 'testpassword'
        }

        response_login = self.client.post('/api/auth/login', data_login)
        # Mendapatkan token
        self.token = f"Bearer {response_login.data['token']['access']}"

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
    
    def test_04_verifikasi_kode_registrasi(self):
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
    
    def test_07_login_sukses(self):
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
    
    def test_08_login_username_salah(self):
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
    
    def test_09_login_kata_sandi_salah(self):
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
    
    def test_10_login_parameter_kurang(self):
        # Parameter kata sandi tidak diisi

        url = '/api/auth/login'

        kredensial = {
            'username': 'testusername'
        }
        
        response = self.client.post(url, kredensial)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Username dan kata sandi harus diisi')