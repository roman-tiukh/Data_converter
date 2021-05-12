import json
import logging

import psycopg2
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from business_register.models.pep_models import Pep

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'fetch and store Peps id from the National agency on corruption prevention'

    def __init__(self, *args, **kwargs):
        self.host = settings.PEP_SOURCE_HOST
        self.port = settings.PEP_SOURCE_PORT
        self.database = settings.PEP_SOURCE_DATABASE
        self.user = settings.PEP_SOURCE_USER
        self.password = settings.PEP_SOURCE_PASSWORD
        self.PEP_QUERY = ("""
            SELECT p.id, MAX(d.declaration_id)
            FROM core_person p
            LEFT JOIN core_declaration d on p.id = d.person_id
            WHERE is_pep = True AND d.nacp_declaration = True AND d.confirmed="a"
            GROUP BY p.id
        """)
        self.all_peps = {getattr(pep, 'source_id'): pep for pep in Pep.objects.filter(is_pep=True)}
        self.all_nacp_id = [getattr(pep, 'nacp_id') for pep in Pep.objects.filter(is_pep=True)]
        self.check_peps = {}

        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        host = self.host
        port = self.port

        connection = psycopg2.connect(
            host=host,
            port=port,
            database=self.database,
            user=self.user,
            password=self.password
        )

        with connection.cursor() as cursor:
            cursor.execute(self.PEP_QUERY)
            for pep_data in cursor.fetchall():
                pep = self.all_peps.get(pep_data[0])
                if pep.nacp_id:
                    continue
                declaration_id = pep_data[1].replace('nacp_', '')
                response = requests.get(settings.NACP_DECLARATION_RETRIEVE + declaration_id)
                if (response.status_code != 200):
                    logger.error(f'cannot find the declaration with id: {declaration_id}')
                    continue
                pep_nacp_id = json.loads(response.text)['user_declarant_id']
                if pep_nacp_id not in self.all_nacp_id:
                    pep.nacp_id = pep_nacp_id
                    pep.save()
                    self.all_nacp_id.append(pep_nacp_id)
                else:
                    self.check_peps[pep.fullname] = pep_nacp_id
                if self.check_peps:
                    logger.info(f'check Peps with NACP id {self.check_peps}')
