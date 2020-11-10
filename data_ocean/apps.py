from django.apps import AppConfig


class DataOceanConfig(AppConfig):
    name = 'data_ocean'

    def ready(self):
        from data_ocean import handlers
