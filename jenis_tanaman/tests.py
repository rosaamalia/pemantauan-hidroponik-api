from rest_framework.test import APITestCase
from .models import JenisTanaman

class JenisTanamanTest(APITestCase):
    def setUp(self):
        jenis_tanaman = [
            JenisTanaman(id=1, nama_tanaman='Tomat', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='path/to/model'),
            JenisTanaman(id=2, nama_tanaman='Selada', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='path/to/model'),
            JenisTanaman(id=3, nama_tanaman='Kangkung', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='path/to/model'),
            JenisTanaman(id=4, nama_tanaman='Stroberi', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='path/to/model'),
            JenisTanaman(id=5, nama_tanaman='Tomat Ceri', foto='image.com', deskripsi='Deskripsi', teks_artikel='Teks artikel', model='path/to/model'),
        ]
        JenisTanaman.objects.bulk_create(jenis_tanaman)

    def test_01_mendapatkan_semua_data_jenis_tanaman(self):
        url = '/api/jenis-tanaman/?page=1'

        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 5)
    
    def test_02_mendapatkan_data_berdasarkan_id_sukses(self):
        id_jenis_tanaman = 1
        url = f'/api/jenis-tanaman/{id_jenis_tanaman}'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['message'], 'Data berhasil diambil.')
        self.assertEqual(response.data['data']['id'], id_jenis_tanaman)
    
    def test_03_mendapatkan_data_berdasarkan_id_gagal(self):
        id_jenis_tanaman = 6
        url = f'/api/jenis-tanaman/{id_jenis_tanaman}'

        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], f"Data jenis tanaman dengan id {id_jenis_tanaman} tidak ditemukan.")
    
    def test_04_mencari_data_dengan_keyword(self):
        keyword = 'tomat'
        url = f'/api/jenis-tanaman/cari?q={keyword}'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 2)