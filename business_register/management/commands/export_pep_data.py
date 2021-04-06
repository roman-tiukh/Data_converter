import os
from datetime import date
import string
import random
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.http import HttpRequest
from rest_framework.request import Request
from business_register.models.pep_models import Pep
from business_register.serializers.company_and_pep_serializers import (
    PepDetailWithoutCheckCompaniesSerializer
)
from data_converter.file_generators import JSONGenerator, XMLGenerator


class Command(BaseCommand):
    help = 'Saves ALL PEPs data to file in "export/" directory'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--format', type=str, default='xml', nargs='?', choices=['xml', 'json'])
        parser.add_argument('-l', '--limit', type=int, nargs='?')
        parser.add_argument('-p', '--pretty', dest='pretty', action='store_true')
        parser.add_argument('-s', '--s3', dest='s3', action='store_true')

    def print(self, message, success=False):
        if success:
            self.stdout.write(self.style.SUCCESS(f'> {message}'))
        else:
            self.stdout.write(f'> {message}')

    def save_to_file(self, data, export_format):
        file_name = f'dataocean_pep_{date.today()}.{export_format}'
        self.print(f'Write to file - "export/{file_name}"')
        file_dir = os.path.join(settings.BASE_DIR, 'export')
        os.makedirs(file_dir, exist_ok=True)
        with open(os.path.join(file_dir, file_name), 'w') as file:
            file.write(data)
        return f'export/{file_name}'

    def save_to_s3bucket(self, data, export_format):
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        file_name = f'dataocean_pep_{date.today()}_{salt}.{export_format}'
        bucket_name = settings.AWS_S3_PEP_EXPORT_BUCKET_NAME
        bucket_region = settings.AWS_S3_REGION_NAME

        self.print(f'Write to file in S3 bucket - "{file_name}"')
        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            region_name=bucket_region,
        )
        s3.Bucket(bucket_name).put_object(
            Key=file_name,
            Body=data,
            ACL='public-read',
            ContentDisposition='attachment',
            ContentType='application/octet-stream',
        )
        url = f'https://{bucket_name}.s3.{bucket_region}.amazonaws.com/{file_name}'
        self.print(f'File URL: {url}', success=True)
        return url

    def handle(self, *args, **options):
        export_format = options['format']
        pretty = options['pretty']
        limit = options['limit']
        s3 = options['s3']
        request = Request(HttpRequest())
        # request._request.GET.setdefault('show_check_companies', 'none')
        # request._request.GET.setdefault('company_relations', 'none')

        count = Pep.objects.count()
        peps = Pep.objects.prefetch_related(
            'from_person_links', 'to_person_links',
            'to_person_links__from_person', 'from_person_links__to_person',
            # 'related_companies__company__company_type',
            # 'related_companies__company__status',
            # 'related_companies__company__founders',
        )
        if limit:
            peps = peps[:limit]

        self.print(f'Start generate data in {export_format} format')
        if export_format == 'json':
            generator = JSONGenerator(indent=2 if pretty else None)
        elif export_format == 'xml':
            generator = XMLGenerator(pretty_print=pretty)
        else:
            raise ValueError(f'Format not allowed = "{export_format}"')

        generator.start()
        i = 1
        for pep in peps.iterator():
            serializer = PepDetailWithoutCheckCompaniesSerializer(pep, context={'request': request})
            generator.add_list_item(serializer.data)
            if i % 10 == 0:
                self.stdout.write(f'Processed {i} of {count}', ending='\r')
            i += 1

        generator.finish()
        data = generator.get_data()

        if s3:
            self.save_to_s3bucket(data, export_format)
        else:
            self.save_to_file(data, export_format)

        self.print('Success!', success=True)
