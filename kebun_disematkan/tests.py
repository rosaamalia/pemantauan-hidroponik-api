from rest_framework.test import APITestCase
from .models import KebunDisematkan
from akun.models import Akun
from kebun.models import Kebun
from jenis_tanaman.models import JenisTanaman

class KebunDisematkanTest(APITestCase):
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

        jenis_tanaman = JenisTanaman.objects.create(id=1, nama_tanaman='Tomat', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='path/to/model')

        kebun = [
            Kebun(id=1, id_akun=self.akun, id_jenis_tanaman=jenis_tanaman, nama_kebun='Kebun Tomat 1', deskripsi='Deskripsi'),
            Kebun(id=2, id_akun=self.akun, id_jenis_tanaman=jenis_tanaman, nama_kebun='Kebun Tomat 2', deskripsi='Deskripsi'),
            Kebun(id=3, id_akun=self.akun, id_jenis_tanaman=jenis_tanaman, nama_kebun='Kebun Tomat 3', deskripsi='Deskripsi'),
        ]
        Kebun.objects.bulk_create(kebun)

    def test_01_update_data_kebun_disematkan_sukses(self):
        url = '/api/kebun-disematkan/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        data = {
            "kebun": [1, 2, 3]
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['message'], 'Data berhasil diperbarui.')
        self.assertEqual(response.data['data']['kebun'], [1, 2, 3])
    
    def test_02_update_data_kebun_disematkan_gagal(self):
        url = '/api/kebun-disematkan/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        data = {
            "kebun": [1, 2, 3]
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
    
    def test_03_mengambil_data_kebun_disematkan_sukses(self):
        KebunDisematkan.objects.filter(id_akun=self.akun.id).update(kebun=[1, 2, 3])

        url = '/api/kebun-disematkan/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['message'], 'Data berhasil diambil.')
        self.assertEqual(response.data['data']['kebun'][0]['id'], 1)
        self.assertEqual(response.data['data']['kebun'][1]['id'], 2)
        self.assertEqual(response.data['data']['kebun'][2]['id'], 3)
    
    def test_04_mengambil_data_kebun_disematkan_gagal(self):
        KebunDisematkan.objects.filter(id_akun=self.akun.id).update(kebun=[1, 2, 3])

        url = '/api/kebun-disematkan/'

        self.client.credentials(HTTP_AUTHORIZATION=self.token_tidak_berlaku)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Token yang diberikan tidak valid untuk semua jenis token')
