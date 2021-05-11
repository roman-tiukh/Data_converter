from business_register.converter.business_converter import BusinessConverter
from business_register.models.pep_models import Pep
from business_register.models.declaration_models import Declaration, Property
import requests
import logging

from django.conf import settings

from data_ocean.utils import format_date_to_yymmdd

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
        self.NO_DATA = ['[Не застосовується]', '[Не відомо]', '[Член сім\'ї не надав інформацію]']
        self.keys = set()

    def save_property_right(self, property, acquisition_date, right_data):
        pass

    def save_property(self, property_data, declaration):
        TYPES = {
            'Інше': Property.OTHER,
            'Земельна ділянка': Property.LAND,
            'Кімната': Property.ROOM,
            'Квартира': Property.APARTMENT,
            'Садовий (дачний) будинок': Property.SUMMER_HOUSE,
            'Житловий будинок': Property.HOUSE,
            'Гараж': Property.GARAGE,
            'Офіс': Property.OFFICE
        }
        # this is for future documentation))
        possible_keys = {'ua_street_extendedstatus', 'postCode_extendedstatus', 'regNumber_extendedstatus',
         'costDate_extendedstatus', 'ua_apartmentsNum_extendedstatus', 'regNumber', 'cityPath', 'person',
         'owningDate', 'ua_houseNum_extendedstatus', 'region_extendedstatus', 'costDate', 'district',
         'costAssessment_extendedstatus', 'district_extendedstatus', 'cost_date_assessment_extendedstatus',
         'sources', 'rights', 'ua_apartmentsNum', 'ua_street', 'objectType', 'otherObjectType', 'ua_cityType',
         'costAssessment', 'ua_postCode_extendedstatus', 'ua_postCode', 'owningDate_extendedstatus',
         'ua_housePartNum_extendedstatus', 'ua_housePartNum', 'loc_engLivingAddress_extendedstatus', 'iteration',
         'ua_buildType', 'loc_engLivingAddress', 'cost_date_assessment', 'city', 'postCode', 'ua_streetType',
         'loc_ukrLivingAddress_extendedstatus', 'totalArea', 'loc_ukrLivingAddress', 'country', 'ua_houseNum',
         'city_extendedstatus', 'ua_streetType_extendedstatus', 'region', 'totalArea_extendedstatus'}

        for data in property_data:
            property_type = TYPES.get(data['objectType'])
            if property_type == Property.OTHER:
                additional_info = data
            else:
                additional_info = ''
            # TODO: add country
            property_country = self.find_country(data['country'])
            property_location = data.get('ua_cityType')
            # TODO: add property_city
            property_city = self.find_city(property_location)
            property_valuation = data.get('costAssessment')
            if not property_valuation and property_valuation in self.NO_DATA:
                # In 2015 there was a separate field 'costDate' or 'cost_date_assessment' with the
                # valuation at the date of acquisition. Now all fields are united
                property_valuation = data.get('costDate')
                if not property_valuation or property_valuation in self.NO_DATA:
                    property_valuation = data.get('cost_date_assessment')
            if property_valuation and property_valuation not in self.NO_DATA:
                    property_valuation = int(property_valuation)
            else:
                property_valuation = None
            property_area = data.get('totalArea')
            if property_area and property_area not in self.NO_DATA:
                property_area = float(property_area.replace(',', '.'))
            else:
                property_area = None
            acquisition_date = format_date_to_yymmdd(data.get('owningDate'))
            property = Property.objects.create(
                declaration=declaration,
                type=property_type,
                additional_info=additional_info,
                area=property_area,
                country=property_country,
                city=property_city,
                valuation=property_valuation,

            )
            self.save_property_right(property, acquisition_date, data['rights'])

    # TODO: retrieve country from Country DB
    def find_country(self, property_country_data):
        pass

    # TODO: extract registration data
    def find_city(self, registration_data):
        pass

    # TODO: save family data with NACP id
    def save_family_data(self, relatives_data, declaration):
        for relative_data in relatives_data:
            relative = relative_data.get('subjectRelation')
            if relative in ['дружина', 'чоловік']:
                spouse = None

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
                # TODO: predict storing changes from the declarant
                if not declaration:
                    declaration = Declaration.objects.create(
                        type=declaration_data['declaration_type'],
                        year=declaration_data['declaration_year'],
                        nacp_declaration_id=declaration_id,
                        nacp_declarant_id=nacp_declarant_id,
                        pep=self.only_peps[nacp_declarant_id],
                    )

                # getting full declaration data
                response = requests.get(settings.NACP_DECLARATION_RETRIEVE + declaration_id)
                if response.status_code != 200:
                    logger.error(
                        f'cannot find declarations with nacp_declaration_id: {declaration_id}'
                    )
                    continue
                detailed_declaration_data = response.json()['data']

                # 'Step_1' - declarant`s personal data
                last_job_title = detailed_declaration_data['step_1']['data'].get('workPost')
                last_employer = detailed_declaration_data['step_1']['data'].get('workPlace')
                registration_data = detailed_declaration_data['step_1']['data'].get('cityType')
                if registration_data:
                    city_of_registration = self.find_city(registration_data)
                else:
                    city_of_registration = None
                # TODO: make a method for extracting residence data

                # 'Step_2' - declarant`s family
                if (detailed_declaration_data['step_2']
                        and not detailed_declaration_data['step_2'].get('isNotApplicable')):
                    self.save_family_data(detailed_declaration_data['step_2']['data'], declaration)

                # 'Step_3' - declarant`s family`s properties
                if (detailed_declaration_data['step_3']
                        and not detailed_declaration_data['step_3'].get('isNotApplicable')):
                    self.save_property(detailed_declaration_data['step_3']['data'], declaration)

                declaration.last_job_title = last_job_title
                declaration.last_employer = last_employer
                declaration.city_of_registration = city_of_registration
                # declaration.save()
