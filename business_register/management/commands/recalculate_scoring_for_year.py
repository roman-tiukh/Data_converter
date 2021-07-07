from django.core.management.base import BaseCommand
from business_register.models.declaration_models import Declaration


class Command(BaseCommand):
    help = '---'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, nargs=1)

    def handle(self, *args, **options):
        year = options['year'][0]
        for declaration in Declaration.objects.filter(year=year):
            declaration.recalculate_scoring()
