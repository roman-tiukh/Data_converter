import os
import json
from datetime import date
from io import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from django.utils.xmlutils import SimplerXMLGenerator
from rest_framework.request import Request
from rest_framework_xml.renderers import XMLRenderer
from business_register.models.pep_models import Pep
from business_register.serializers.company_and_pep_serializers import (
    PepDetailSerializer, PepListSerializer, PepShortSerializer
)


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
        if export_format == 'json':
            raise NotImplementedError()

        request = Request(HttpRequest())
        request._request.GET.setdefault('show_check_companies', 'none')
        # request._request.GET.setdefault('company_relations', 'none')
        i = 1
        renderer = XMLRenderer()
        stream = StringIO()
        xml = SimplerXMLGenerator(stream, XMLRenderer.charset)
        xml.startDocument()
        xml.startElement(XMLRenderer.root_tag_name, {})

        count = Pep.objects.count()
        peps = Pep.objects.prefetch_related(
            'from_person_links', 'to_person_links',
            'to_person_links__from_person', 'from_person_links__to_person',
            # 'related_companies__company__company_type',
            # 'related_companies__company__status',
            # 'related_companies__company__founders',
        )

        self.print(f'Start generate data in {export_format} format')
        for pep in peps.iterator():
            serializer = PepDetailSerializer(pep, context={'request': request})

            if export_format == 'json':
                data = json.dumps(serializer.data, ensure_ascii=False)
            elif export_format == 'xml':
                xml.startElement(XMLRenderer.item_tag_name, {})
                renderer._to_xml(xml, serializer.data)
                xml.endElement(XMLRenderer.item_tag_name)
            else:
                raise ValueError(f'Format not allowed = "{export_format}"')

            self.stdout.write(f'Processed {i} of {count}', ending='\r')
            i += 1

        xml.endElement(XMLRenderer.root_tag_name)
        xml.endDocument()
        data = stream.getvalue()

        file_name = f'dataocean_pep_{date.today()}.{export_format}'
        self.print(f'Write to file - "export/{file_name}"')
        file_dir = os.path.join(settings.BASE_DIR, 'export')
        os.makedirs(file_dir, exist_ok=True)
        with open(os.path.join(file_dir, file_name), 'w') as file:
            file.write(data)

        self.print('Success!', success=True)
