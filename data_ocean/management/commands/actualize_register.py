from django.core.management.base import BaseCommand
from data_ocean.models import Register


class Command(BaseCommand):
    help = 'actualize registers updates in Register table'

    def handle(self):
        Register.actualize_updates()
