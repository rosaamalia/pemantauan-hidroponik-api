# Pemantauan Hidroponik API

## Menghubungkan ke database

Pada file `/api/settings.py`, tambahkan informasi database ke variabel `DATABASE`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}
```

Informasi database didefinisikan di dalam file `/env` berikut.

```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
```

Untuk memastikan database sudah terhubung, jalankan command

```
python manage.py dbshell
```

nanti tampilannya seperti ini (contoh ada warning):

```
psql (15.2)
WARNING: Console code page (437) differs from Windows code page (1252)
         8-bit characters might not work correctly. See psql reference
         page "Notes for Windows users" for details.
Type "help" for help.

pemantauan-hidroponik=# \q
```

Jika belum, pastikan hal-hal berikut sudah terpenuhi:

- `psycopg2-binary` sudah ter-install dengan `pip install psycopg2-binary`
- `psql` sudah terdefinisikan di path variable

### Cara menggunakan .env

1. Install library `python-dotenv`
   ```bash
   pip install python-dotenv
   ```
2. Pada file yang membutuhkan variabel env, tambahkan baris kode berikut

   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()
   ```

3. Buat file `.env` dan variabelnya
4. Cara menggunakan variabel env, dapat merujuk ke sub-chapter [Menghubungkan ke database](#menghubungkan-ke-database)
