from django.core.management.base import BaseCommand
from data_ocean.models import Register


class Command(BaseCommand):
    help = 'actualize registers updates in Register table'

    def handle(self, *args, **options):
        Register.actualize_updates()
