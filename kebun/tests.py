from rest_framework.test import APITestCase
from akun.models import Akun
from .models import Kebun, JenisTanaman

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
        self.token_tidak_berlaku = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5Mjk2NDQwOSwiaWF0IjoxNjg1MTg4NDA5LCJqdGkiOiJlYzg4ZGZkZDQ1YWQ0OTNmYjU4MTdkNGJkNzM0MzMxOCIsInVzZXJfaWQiOjIxfQ.ZrMKLng_eSX-DpFfT7lSz6r1mzEdXUFqT3tpq61JhAA'

        jenis_tanaman = JenisTanaman.objects.create(id=1, nama_tanaman='Tomat', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='path/to/model')

        kebun = [
            Kebun(id_akun=self.akun, id_jenis_tanaman=jenis_tanaman, nama_kebun='Kebun Tomat 1', deskripsi='Deskripsi'),
            Kebun(id_akun=self.akun, id_jenis_tanaman=jenis_tanaman, nama_kebun='Kebun Tomat 2', deskripsi='Deskripsi'),
            Kebun(id_akun=self.akun, id_jenis_tanaman=jenis_tanaman, nama_kebun='Kebun Tomat 3', deskripsi='Deskripsi'),
        ]
        Kebun.objects.bulk_create(kebun)

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
        self.assertEqual(response.data['detail'], 'Pengguna tidak ditemukan')
    
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
        self.assertEqual(response.data['detail'], 'Pengguna tidak ditemukan')
    
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
