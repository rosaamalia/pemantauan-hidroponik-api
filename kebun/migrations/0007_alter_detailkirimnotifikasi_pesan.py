# Generated by Django 4.0.10 on 2023-05-27 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kebun', '0006_remove_detailkirimnotifikasi_batas_parameter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailkirimnotifikasi',
            name='pesan',
            field=models.TextField(blank=True, null=True),
        ),
    ]
