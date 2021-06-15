from django.core.management.base import BaseCommand
from business_register.converter.kved import KvedConverter


class Command(BaseCommand):
    help = 'Fill kved_section name_en field'

    def handle(self, *args, **options):
        KvedConverter().fill_name_en_sections()
