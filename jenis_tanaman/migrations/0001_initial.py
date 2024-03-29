# Generated by Django 4.0.10 on 2023-05-20 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JenisTanaman',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_tanaman', models.CharField(max_length=50, unique=True)),
                ('foto', models.CharField(max_length=256)),
                ('deskripsi', models.CharField(max_length=80)),
                ('teks_artikel', models.TextField()),
                ('model', models.CharField(max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'jenis_tanaman',
            },
        ),
    ]
