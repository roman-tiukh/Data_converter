from django.core.management.base import BaseCommand
from business_register.converter.fop_full import FopFullConverter


class Command(BaseCommand):
    help = 'Saves FOP data into DB'

    def add_arguments(self, parser):
        parser.add_argument('start_index', nargs='?', type=int, default=0)

    def handle(self, *args, **options):
        FopFullConverter().process(options['start_index'])
