from django.apps import AppConfig


class BusinessRegisterConfig(AppConfig):
    name = 'business_register'

    def ready(self):
        import business_register.pep_scoring.rules
