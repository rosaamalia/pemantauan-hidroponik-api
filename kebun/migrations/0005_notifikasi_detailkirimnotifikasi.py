# Generated by Django 4.0.10 on 2023-05-27 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kebun', '0004_datakebun'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifikasi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ph_min', models.FloatField(default=0)),
                ('ph_max', models.FloatField(default=0)),
                ('temperatur_min', models.FloatField(default=0)),
                ('temperatur_max', models.FloatField(default=0)),
                ('tds_min', models.FloatField(default=0)),
                ('tds_max', models.FloatField(default=0)),
                ('intensitas_cahaya_min', models.FloatField(default=0)),
                ('intensitas_cahaya_max', models.FloatField(default=0)),
                ('kelembapan_min', models.FloatField(default=0)),
                ('kelembapan_max', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id_kebun', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='kebun.kebun')),
            ],
            options={
                'db_table': 'notifikasi',
            },
        ),
        migrations.CreateModel(
            name='DetailKirimNotifikasi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter', models.CharField(choices=[('ph', 'pH'), ('temperatur', 'temperatur udara'), ('tds', 'TDS'), ('intensitas_cahaya', 'intensitas cahaya'), ('kelembapan', 'kelembapan udara')], max_length=17)),
                ('batas_parameter', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id_notifikasi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kebun.notifikasi')),
            ],
            options={
                'db_table': 'detail_kirim_notifikasi',
            },
        ),
    ]
