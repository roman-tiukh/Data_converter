import json
import logging

import psycopg2
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from business_register.models.pep_models import Pep, RelatedPersonsLink

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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


def is_same_full_name(relative_data, pep, declaration_id):
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
                logger.error(f'Check related person data ({relative_data}) from declaration '
                             f'with NACP id {declaration_id}')
                return False
            last_name = splitted_names[0]
            first_name = splitted_names[1]
            if len(splitted_names) == 3:
                middle_name = splitted_names[2]
    if not last_name or not first_name:
        print(relative_data)
    if not middle_name:
        middle_name = ''

    return (
            pep.last_name.capitalize() == last_name
            and pep.first_name.capitalize() == first_name
            and pep.middle_name.capitalize() == middle_name
    )


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
            WHERE is_pep = True AND d.nacp_declaration = True AND d.confirmed='a'
            GROUP BY p.id
        """)
        self.all_peps = {getattr(pep, 'source_id'): pep for pep in Pep.objects.filter(is_pep=True)}
        self.all_nacp_id = [getattr(pep, 'nacp_id') for pep in Pep.objects.filter(is_pep=True)]
        self.check_peps = []

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
                declaration_id = pep_data[1].replace('nacp_', '')
                response = requests.get(settings.NACP_DECLARATION_RETRIEVE + declaration_id)
                if response.status_code != 200:
                    logger.error(f'cannot find the declaration with id: {declaration_id}')
                    continue
                declaration_data = json.loads(response.text)

                if not pep.nacp_id:
                    # storing PEP nacp_id from declarations list
                    pep_nacp_id = declaration_data['user_declarant_id']
                    if not isinstance(pep_nacp_id, int) or pep_nacp_id == 0:
                        logger.error(f'Check invalid declarant NACP id ({relative_data}) from declaration '
                                     f'with NACP id {declaration_id}')
                    else:
                        pep.nacp_id = pep_nacp_id
                        pep.save()

                    # additional check of matching PEP`s last_name and first_name
                    # last_name = declaration_data['data']['step_1']['data'].get('lastname')
                    # first_name = declaration_data['data']['step_1']['data'].get('firstname')
                    # if (
                    #         pep.last_name != last_name.lower()
                    #         or pep.first_name != first_name.lower()
                    # ):
                    #     logger.error(
                    #         f'PEP data from our DB with id {pep.id}: {pep.last_name} {pep.first_name}, '
                    #         f'from declaration: {last_name} {first_name}')
                    #     self.check_peps.append(
                    #         f'PEP data from our DB with id {pep.id}: {pep.last_name} {pep.first_name}, '
                    #         f'from declaration: {last_name} {first_name}')
                    #     continue
                # TODO: investigate PEPs without nacp_id

                # storing RelatedPerson (not PEP) NACP id from PEP declaration
                detailed_declaration_data = declaration_data['data']
                if (detailed_declaration_data['step_2']
                        and not detailed_declaration_data['step_2'].get('isNotApplicable')):
                    for relative_data in detailed_declaration_data['step_2']['data']:
                        to_person_relationship_type = relative_data.get('subjectRelation')
                        related_person_links = RelatedPersonsLink.objects.filter(
                            from_person=pep,
                            to_person_relationship_type=to_person_relationship_type)
                        for link in related_person_links:
                            # escaping RelatedPerson that already has nacp_id
                            if link.to_person.nacp_id:
                                continue
                            related_person = link.to_person
                            if is_same_full_name(
                                    relative_data,
                                    related_person,
                                    declaration_id
                            ):
                                related_person_nacp_id = relative_data.get('id')
                                if not isinstance(related_person_nacp_id, int) or related_person_nacp_id == 0:
                                    logger.error(f'Check invalid declarant NACP id ({related_person_nacp_id}) from declaration '
                                                 f'with NACP id {declaration_id}')
                                else:
                                    related_person.nacp_id = related_person_nacp_id
                                    related_person.save()
