from django.core.management.base import BaseCommand
from business_register.converter.company_converters.ukr_company_full import UkrCompanyFullConverter


class Command(BaseCommand):
    help = 'Saves Companies data into DB'

    def add_arguments(self, parser):
        parser.add_argument('start_index', nargs='?', type=int, default=0)

    def handle(self, *args, **options):
        UkrCompanyFullConverter().process(options['start_index'])
