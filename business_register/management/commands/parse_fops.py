from django.core.management.base import BaseCommand
from business_register.converter.fop import FopConverter


class Command(BaseCommand):
    help = 'Saves FOP data into DB'

    def add_arguments(self, parser):
        parser.add_argument('start_index', nargs='?', type=int, default=0)

    def handle(self, *args, **options):
        FopConverter().process_full(options['start_index'])
