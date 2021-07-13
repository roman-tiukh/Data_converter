import json
import psycopg2
import requests
import sshtunnel
from django.conf import settings
from django.core.management.base import BaseCommand

from business_register.models.pep_models import Pep


# possible_keys = ['previous_eng_middlename_extendedstatus', 'street_extendedstatus', 'eng_full_address',
#  'district_extendedstatus', 'birthday_extendedstatus', 'housePartNum', 'district', 'country_extendedstatus',
#  'ukr_full_name', 'taxNumber_extendedstatus', 'eng_middlename_extendedstatus', 'middlename_extendedstatus',
#  'eng_full_name', 'citizenship_extendedstatus', 'id', 'previous_lastname', 'previous_eng_lastname',
#  'unzr_extendedstatus', 'eng_identification_code_extendedstatus', 'eng_middlename', 'region',
#  'identificationCode_extendedstatus', 'postCode_extendedstatus', 'city_extendedstatus',
#  'apartmentsNum_extendedstatus', 'ukr_full_address_extendedstatus', 'unzr', 'previous_eng_firstname', 'usage',
#  'eng_full_address_extendedstatus', 'eng_identification_code', 'cityType', 'lastname',
#  'houseNum_extendedstatus', 'eng_lastname', 'changedName', 'country', 'housePartNum_extendedstatus', 'cityPath',
#  'firstname', 'passportCode', 'ukr_full_address', 'taxNumber', 'eng_firstname', 'previous_middlename',
#  'houseNum', 'apartmentsNum', 'previous_middlename_extendedstatus', 'previous_firstname', 'passport',
#  'identificationCode', 'no_taxNumber', 'region_extendedstatus', 'street', 'birthday', 'streetType',
#  'middlename', 'previous_eng_middlename', 'subjectRelation', 'citizenship', 'city', 'streetType_extendedstatus',
#  'postCode', 'passport_extendedstatus']
from data_ocean.savepoint import Savepoint


class InvalidRelativeData(Exception):
    def __init__(self, relative_data):
        self.relative_data = relative_data

    def __str__(self):
        return f'Check related person data ({self.relative_data})'


def is_same_full_name(relative_data, pep):
    last_name = relative_data.get('lastname')
    first_name = relative_data.get('firstname')
    middle_name = relative_data.get('middlename')
    if not last_name:
        last_name = relative_data.get('eng_lastname')
    if not first_name:
        first_name = relative_data.get('eng_firstname')
    if not middle_name:
        middle_name = relative_data.get('eng_middlename')
    if not last_name and not first_name:
        full_name = relative_data.get('ukr_full_name')
        if not full_name:
            full_name = relative_data.get('eng_full_name')
        if full_name:
            splitted_names = full_name.split(' ')
            if len(splitted_names) < 2:
                raise InvalidRelativeData(relative_data)
            last_name = splitted_names[0]
            first_name = splitted_names[1]
            if len(splitted_names) == 3:
                middle_name = splitted_names[2]
    if not last_name or not first_name:
        raise InvalidRelativeData(relative_data)
    if not middle_name:
        middle_name = ''
    return (
            pep.last_name == last_name.lower().strip()
            and pep.first_name == first_name.lower().strip()
            and pep.middle_name == middle_name.lower().strip()
    )


# TODO: investigate PEPs without nacp_id
class Command(BaseCommand):
    help = 'fetch and store Peps id from the National agency on corruption prevention'

    def __init__(self, *args, **kwargs):
        self.savepoint = Savepoint('peps_nacp_ids')
        self.host = settings.PEP_SOURCE_HOST
        self.port = settings.PEP_SOURCE_PORT
        self.database = settings.PEP_SOURCE_DATABASE
        self.user = settings.PEP_SOURCE_USER
        self.password = settings.PEP_SOURCE_PASSWORD
        self.PEP_QUERY = ("""
                SELECT p.id,
                       d.declaration_id
                FROM core_person p
                LEFT JOIN core_declaration d ON p.id = d.person_id
                WHERE is_pep = TRUE
                  AND d.nacp_declaration = TRUE
                  AND d.confirmed='a'
                GROUP BY p.id,
                         d.declaration_id
                ORDER BY p.id
        """)
        self.all_peps = {getattr(pep, 'source_id'): pep for pep in Pep.objects.filter(
            is_pep=True
        )}
        self.all_nacp_id = [getattr(pep, 'nacp_id') for pep in Pep.objects.filter(is_pep=True)]
        self.check_peps = []

        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    def process(self, host=None, port=None):
        host = host or self.host
        port = port or self.port

        self.stdout.write(f'business_pep: psycopg2 connect to {host}:{port}...')
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        cursor = connection.cursor()
        cursor.execute(self.PEP_QUERY)
        i = 0
        rows = cursor.fetchall()
        count = len(rows)
        for pep_data in rows:
            i += 1
            self.stdout.write(f'\rProgress: {i} of {count}', ending='')
            self.stdout.flush()
            pep_source_id = pep_data[0]
            if self.savepoint.has(pep_source_id):
                continue
            pep = self.all_peps.get(pep_source_id)
            if not pep:
                self.stdout.write(f'No PEP from ANTAC`s DB with id={pep_data[0]} in our database')
                self.savepoint.add(pep_source_id)
                continue
            declaration_id = pep_data[1].replace('nacp_', '')
            response = requests.get(settings.NACP_DECLARATION_RETRIEVE + declaration_id)
            if response.status_code != 200:
                self.stdout.write(f'cannot find the declaration with id: {declaration_id}')
                self.savepoint.add(pep_source_id)
                continue
            declaration_data = json.loads(response.text)

            # storing PEP nacp_id from declarations list
            pep_nacp_id = declaration_data.get('user_declarant_id')
            if not isinstance(pep_nacp_id, int) or not pep_nacp_id:
                self.stdout.write(f'Check invalid declarant NACP id ({pep_nacp_id}) from declaration '
                                  f'with NACP id {declaration_id}')
                self.savepoint.add(pep_source_id)
                continue
            elif pep_nacp_id not in pep.nacp_id:
                pep.nacp_id.append(pep_nacp_id)
                pep.save()
            self.savepoint.add(pep_source_id)

            # additional check of matching PEP`s last_name and first_name
            # last_name = declaration_data['data']['step_1']['data'].get('lastname')
            # first_name = declaration_data['data']['step_1']['data'].get('firstname')
            # if (
            #         pep.last_name != last_name.lower()
            #         or pep.first_name != first_name.lower()
            # ):
            #     self.stdout.write(
            #         f'PEP data from our DB with id {pep.id}: {pep.last_name} {pep.first_name}, '
            #         f'from declaration: {last_name} {first_name}')
            #     self.check_peps.append(
            #         f'PEP data from our DB with id {pep.id}: {pep.last_name} {pep.first_name}, '
            #         f'from declaration: {last_name} {first_name}')
            #     continue

        self.savepoint.close()
        self.stdout.write()
        self.stdout.write('Done!')

    def handle(self, *args, **options):
        self.stdout.write(f'business_pep: use SSH tunnel: {settings.PEP_SOURCE_USE_SSH}')

        if not settings.PEP_SOURCE_USE_SSH:
            self.process()
            return

        sshtunnel.TUNNEL_TIMEOUT = settings.PEP_TUNNEL_TIMEOUT
        sshtunnel.SSH_TIMEOUT = settings.PEP_SSH_TIMEOUT
        with sshtunnel.SSHTunnelForwarder(
                (settings.PEP_SSH_SERVER_IP, settings.PEP_SSH_SERVER_PORT),
                ssh_username=settings.PEP_SSH_USERNAME,
                ssh_pkey=settings.PEP_SSH_PKEY,
                remote_bind_address=(self.host, self.port),
                # local_bind_address=(settings.PEP_LOCAL_SOURCE_HOST, settings.PEP_LOCAL_SOURCE_PORT)
        ) as tunnel:
            self.stdout.write(
                f'business_pep: tunnel is active: {tunnel.is_active} on '
                f'{tunnel.local_bind_host}:{tunnel.local_bind_port}'
            )
            self.process(
                host=tunnel.local_bind_host,
                port=tunnel.local_bind_port,
            )

