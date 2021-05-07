from business_register.converter.business_converter import BusinessConverter
from business_register.models.pep_models import Pep
from business_register.models.declaration_models import Declaration
import requests
import logging

from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DeclarationConverter(BusinessConverter):

    def __init__(self):
        self.only_peps = {pep.source_id: pep for pep in Pep.objects.filter(is_pep=True)}
        self.all_declarations = self.put_objects_to_dict(
            'nacp_declaration_id',
            'business_register',
            'Declaration'
        )

    # TODO: extract registration data
    def find_city(self, registration_data):
        pass

    def find_spouse(self, relatives_data):
        for relative_data in relatives_data:
            relative = relative_data.get('subjectRelation')
            if relative in ['дружина', 'чоловік']:
                spouse_fullname = f"{relative_data['lastname']} {relative_data['firstname']} {relative_data['middlename']}"
                return spouse_fullname.lower()
        return None

    def save_or_update_declaration(self):
        for nacp_declarant_id in self.only_peps:
            # getting general info including declaration id
            response = requests.get(
                f'{settings.NACP_DECLARATION_LIST}?user_declarant_id={nacp_declarant_id}'
            )
            if response.status_code != 200:
                logger.error(
                    f'cannot find declarations of the PEP with nacp_declarant_id: {nacp_declarant_id}'
                )
                continue
            for declaration_data in response.json()['data']:
                declaration_id = declaration_data['id']
                declaration = self.all_declarations.get(declaration_id)
                # ToDo: predict storing changes from the declarant
                if declaration:
                    continue
                declaration = Declaration.objects.create(
                    type=declaration_data['declaration_type'],
                    year=declaration_data['declaration_year'],
                    nacp_declaration_id=declaration_id,
                    nacp_declarant_id=nacp_declarant_id,
                    pep=self.only_peps[nacp_declarant_id],
                    last_job_title=declaration_data['data']['step_1']['data']['workPost'],
                    last_employer=declaration_data['data']['step_1']['data']['workPlace'],
                )
                # getting full declaration data
                response = requests.get(settings.NACP_DECLARATION_RETRIEVE + declaration_id)
                if response.status_code != 200:
                    logger.error(
                        f'cannot find declarations with nacp_declaration_id: {declaration_id}'
                    )
                    continue
                detailed_declaration_data = response.json()['data']
                registration_data = detailed_declaration_data['step_1']['data'].get('cityType')
                if registration_data:
                    city_of_registration = self.find_city(registration_data)
                # ToDo: make a method for extracting residence data
                if (detailed_declaration_data['step_2']
                        and not detailed_declaration_data['step_2'].get('isNotApplicable')):
                    spouse = self.find_spouse(detailed_declaration_data['step_2']['data'])
