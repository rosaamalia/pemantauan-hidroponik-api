from django.apps import AppConfig


class DataKebunConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_kebun'

    def ready(self):
        import data_kebun.signals