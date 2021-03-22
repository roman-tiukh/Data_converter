import os
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from rest_framework.request import Request
from business_register.models.pep_models import Pep
from business_register.serializers.company_and_pep_serializers import (
    PepDetailSerializer,
)
from data_converter.file_generators import JSONGenerator, XMLGenerator


class Command(BaseCommand):
    help = 'Saves ALL PEPs data to file in "export/" directory'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--format', type=str, default='xml', nargs='?', choices=['xml', 'json'])

    def print(self, message, success=False):
        if success:
            self.stdout.write(self.style.SUCCESS(f'> {message}'))
        else:
            self.stdout.write(f'> {message}')

    def handle(self, *args, **options):
        export_format = options['format']

        request = Request(HttpRequest())
        request._request.GET.setdefault('show_check_companies', 'none')
        # request._request.GET.setdefault('company_relations', 'none')

        count = Pep.objects.count()
        peps = Pep.objects.prefetch_related(
            'from_person_links', 'to_person_links',
            'to_person_links__from_person', 'from_person_links__to_person',
            # 'related_companies__company__company_type',
            # 'related_companies__company__status',
            # 'related_companies__company__founders',
        )

        self.print(f'Start generate data in {export_format} format')
        if export_format == 'json':
            generator = JSONGenerator()
        elif export_format == 'xml':
            generator = XMLGenerator(pretty_print=True)
        else:
            raise ValueError(f'Format not allowed = "{export_format}"')

        generator.start()
        i = 1
        for pep in peps.iterator():
            serializer = PepDetailSerializer(pep, context={'request': request})
            generator.add_list_item(serializer.data)
            if i % 10 == 0:
                self.stdout.write(f'Processed {i} of {count}', ending='\r')
            i += 1

        generator.finish()
        data = generator.get_data()

        file_name = f'dataocean_pep_{date.today()}.{export_format}'
        self.print(f'Write to file - "export/{file_name}"')
        file_dir = os.path.join(settings.BASE_DIR, 'export')
        os.makedirs(file_dir, exist_ok=True)
        with open(os.path.join(file_dir, file_name), 'w') as file:
            file.write(data)

        self.print('Success!', success=True)
