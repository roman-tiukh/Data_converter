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
from business_register.serializers.company_and_pep_serializers import PepDetailSerializer


class CommandBeta(BaseCommand):
    help = 'Saves ALL PEPs data to file in "export/" directory'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--format', type=str, default='json', nargs='?', choices=['xml', 'json'])

    def print(self, message, success=False):
        if success:
            self.stdout.write(self.style.SUCCESS(f'> {message}'))
        else:
            self.stdout.write(f'> {message}')

    def handle(self, *args, **options):
        export_format = options['format']
        self.print('Get all PEPs from DB')
        peps = Pep.objects.all()

        self.print('Start serialize')
        serializer = PepDetailSerializer(
            peps, many=True,
            context={'request': Request(HttpRequest())}
        )

        self.print(f'Dump data to {export_format} format')
        if export_format == 'json':
            data = json.dumps(serializer.data, ensure_ascii=False)
        elif export_format == 'xml':
            data = XMLRenderer().render(serializer.data)
            # TODO: prettify?
            # xmldom = etree.fromstring(data.encode('utf-8'), parser=etree.XMLParser(encoding='utf-8'))
            # data = etree.tostring(
            #     xmldom, pretty_print=True,
            #     doctype='<?xml version="1.0" encoding="utf-8"?>'
            # )
            # data = data.decode('utf-8')
        else:
            raise ValueError(f'Format not allowed = "{export_format}"')

        file_name = f'dataocean_pep_{date.today()}.{export_format}'
        self.print(f'Write to file - "export/{file_name}"')
        file_dir = os.path.join(settings.BASE_DIR, 'export')
        os.makedirs(file_dir, exist_ok=True)
        with open(os.path.join(file_dir, file_name), 'w') as file:
            file.write(data)

        self.print('Success!', success=True)


class Command(BaseCommand):
    help = 'Saves ALL PEPs data to file in "export/" directory'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--format', type=str, default='json', nargs='?', choices=['xml', 'json'])

    def print(self, message, success=False):
        if success:
            self.stdout.write(self.style.SUCCESS(f'> {message}'))
        else:
            self.stdout.write(f'> {message}')

    def handle(self, *args, **options):
        export_format = options['format']
        self.print('Start parsing')
        i = 1
        renderer = XMLRenderer()
        stream = StringIO()
        xml = SimplerXMLGenerator(stream, XMLRenderer.charset)
        xml.startDocument()
        xml.startElement(XMLRenderer.root_tag_name, {})

        for pep in Pep.objects.iterator():
            serializer = PepDetailSerializer(pep, context={'request': Request(HttpRequest())})
            self.stdout.write(f'{i}', ending='\r')

            if export_format == 'json':
                data = json.dumps(serializer.data, ensure_ascii=False)
            elif export_format == 'xml':
                renderer._to_xml(xml, serializer.data)
            else:
                raise ValueError(f'Format not allowed = "{export_format}"')

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
