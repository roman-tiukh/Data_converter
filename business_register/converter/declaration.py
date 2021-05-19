import logging

import requests
from django.conf import settings

from business_register.converter.business_converter import BusinessConverter
from business_register.models.declaration_models import Declaration, Property
from business_register.models.pep_models import Pep, RelatedPersonsLink
from data_ocean.utils import format_date_to_yymmdd
from location_register.models.address_models import Country
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity

from business_register.management.commands.fetch_peps_nacp_id import is_same_full_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DeclarationConverter(BusinessConverter):

    def __init__(self):
        self.only_peps = {pep.nacp_id: pep for pep in Pep.objects.filter(
            is_pep=True,
            nacp_id__isnull=False
        )}
        self.all_declarations = self.put_objects_to_dict(
            'nacp_declaration_id',
            'business_register',
            'Declaration'
        )
        self.NO_DATA = ['[Не застосовується]', '[Не відомо]', '[Член сім\'ї не надав інформацію]']
        self.keys = set()

    def save_property_right(self, property, acquisition_date, rights_data):
        for data in rights_data:
            data

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
        # possible_keys = [
        #     'ua_street_extendedstatus', 'postCode_extendedstatus', 'regNumber_extendedstatus',
        #     'costDate_extendedstatus', 'ua_apartmentsNum_extendedstatus', 'regNumber', 'cityPath',
        #     'person',
        #     'owningDate', 'ua_houseNum_extendedstatus', 'region_extendedstatus', 'costDate', 'district',
        #     'costAssessment_extendedstatus', 'district_extendedstatus',
        #     'cost_date_assessment_extendedstatus',
        #     'sources', 'rights', 'ua_apartmentsNum', 'ua_street', 'objectType', 'otherObjectType',
        #     'ua_cityType',
        #     'costAssessment', 'ua_postCode_extendedstatus', 'ua_postCode', 'owningDate_extendedstatus',
        #     'ua_housePartNum_extendedstatus', 'ua_housePartNum', 'loc_engLivingAddress_extendedstatus',
        #     'iteration',
        #     'ua_buildType', 'loc_engLivingAddress', 'cost_date_assessment', 'city', 'postCode',
        #     'ua_streetType',
        #     'loc_ukrLivingAddress_extendedstatus', 'totalArea', 'loc_ukrLivingAddress', 'country',
        #     'ua_houseNum',
        #     'city_extendedstatus', 'ua_streetType_extendedstatus', 'region', 'totalArea_extendedstatus'
        # ]

        for data in property_data:
            property_type = TYPES.get(data['objectType'])
            if property_type == Property.OTHER:
                property_additional_info = data
            else:
                property_additional_info = ''
            # TODO: add country
            property_country = self.find_country(data['country'], declaration)
            property_location = data.get('ua_cityType')
            # TODO: add property_city
            property_city = self.find_city(property_location, declaration)
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
                additional_info=property_additional_info,
                area=property_area,
                country=property_country,
                city=property_city,
                valuation=property_valuation,

            )
            self.save_property_right(property, acquisition_date, data['rights'])

    # TODO: retrieve country from Country DB
    def find_country(self, property_country_data, declaration):
        print(declaration.nacp_declaration_id)
        if property_country_data.isdigit():
            country = Country.objects.filter(nacp_id=property_country_data).first()
            if country:
                return country
            else:
                logger.error(
                    f'Cannot find country id {property_country_data} in '
                    f'nacp_declaration_id {declaration.nacp_declaration_id}'
                )
        else:
            logger.error(
                f'Invalid value {property_country_data} in nacp_declaration_id {declaration.nacp_declaration_id}'
            )

    def split_address_data(self, address_data):
        parts = address_data.lower().split(' / ')
        region = district = city = ''
        country = parts[len(parts) - 1]
        parts = parts[:-1]
        city_region = ['київ', 'севастополь']
        for part in parts:
            if '/' in part:
                part = part.split('/')[0]
            if 'район' in part:
                district = part
            elif 'область' in part:
                region = part
            elif part in city_region:
                city = region = part
            else:
                city = part
        return city, region, district

    def find_city(self, address_data, declaration):
        city, region, district = self.split_address_data(address_data)
        ratu_region = RatuRegion.objects.filter(name=region).first()
        ratu_district = RatuDistrict.objects.filter(name=district, region=ratu_region).first()
        if region and not ratu_region:
            logger.error(f'cannot find region {region} in nacp_declaration_id {declaration.nacp_declaration_id}')
        if district and not ratu_district:
            logger.error(f'cannot find district {district} in nacp_declaration_id {declaration.nacp_declaration_id}')
        else:
            city_of_registration = RatuCity.objects.filter(
                name=city,
                region=ratu_region,
                district=ratu_district
            ).first()
            return city_of_registration
        logger.error(f'Cannot find city in nacp_declaration_id {declaration.nacp_declaration_id}')

    # possible_keys = [
    #     'previous_eng_middlename_extendedstatus', 'street_extendedstatus', 'eng_full_address',
    #     'district_extendedstatus', 'birthday_extendedstatus', 'housePartNum', 'district', 'country_extendedstatus',
    #     'ukr_full_name', 'taxNumber_extendedstatus', 'eng_middlename_extendedstatus', 'middlename_extendedstatus',
    #     'eng_full_name', 'citizenship_extendedstatus', 'id', 'previous_lastname', 'previous_eng_lastname',
    #     'unzr_extendedstatus', 'eng_identification_code_extendedstatus', 'eng_middlename', 'region',
    #     'identificationCode_extendedstatus', 'postCode_extendedstatus', 'city_extendedstatus',
    #     'apartmentsNum_extendedstatus', 'ukr_full_address_extendedstatus', 'unzr', 'previous_eng_firstname', 'usage',
    #     'eng_full_address_extendedstatus', 'eng_identification_code', 'cityType', 'lastname',
    #     'houseNum_extendedstatus', 'eng_lastname', 'changedName', 'country', 'housePartNum_extendedstatus', 'cityPath',
    #     'firstname', 'passportCode', 'ukr_full_address', 'taxNumber', 'eng_firstname', 'previous_middlename',
    #     'houseNum', 'apartmentsNum', 'previous_middlename_extendedstatus', 'previous_firstname', 'passport',
    #     'identificationCode', 'no_taxNumber', 'region_extendedstatus', 'street', 'birthday', 'streetType',
    #     'middlename', 'previous_eng_middlename', 'subjectRelation', 'citizenship', 'city', 'streetType_extendedstatus',
    #     'postCode', 'passport_extendedstatus'
    # ]
    # TODO: maybe we should simplify spouse to CharField with full name
    def save_spouse(self, relatives_data, pep, declaration):
        SPOUSE_TYPES = ['дружина', 'чоловік']
        # TODO: decide should we store new Pep that not spouse from relatives_data
        for relative_data in relatives_data:
            to_person_relationship_type = relative_data.get('subjectRelation')
            if to_person_relationship_type in SPOUSE_TYPES:
                spouse = None
                nacp_id = relative_data.get('id')
                if nacp_id:
                    spouse = Pep.objects.filter(nacp_id=nacp_id).first()
                if not spouse:
                    link_from_our_db = RelatedPersonsLink.objects.filter(
                        from_person=pep,
                        to_person_relationship_type=to_person_relationship_type,
                    ).first()
                    if not link_from_our_db:
                        # TODO: decide should we store new Pep here
                        break
                    else:
                        spouse_from_our_db = link_from_our_db.to_person
                        if not is_same_full_name(
                                relative_data,
                                spouse_from_our_db,
                                declaration.id
                        ):
                            break
                        else:
                            spouse = spouse_from_our_db
                if spouse:
                    declaration.spouse = spouse
                    declaration.save()
                    break

    def save_or_update_declaration(self):
        for nacp_declarant_id in self.only_peps:
            # getting general info including declaration id
            response = requests.get(
                f'{settings.NACP_DECLARATION_LIST}?user_declarant_id={nacp_declarant_id}'
            )
            declarations_data = response.json().get('data')
            if response.status_code != 200 or not declarations_data:
                logger.error(
                    f'cannot find declarations of the PEP with nacp_declarant_id: {nacp_declarant_id}'
                )
                continue
            pep = self.only_peps[nacp_declarant_id]
            for declaration_data in declarations_data:
                declaration_id = declaration_data['id']
                declaration = self.all_declarations.get(declaration_id)
                # TODO: predict storing changes from the declarant
                if declaration:
                    continue
                else:
                    declaration = Declaration.objects.create(
                        type=declaration_data['declaration_type'],
                        year=declaration_data['declaration_year'],
                        nacp_declaration_id=declaration_id,
                        nacp_declarant_id=nacp_declarant_id,
                        pep=pep,
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
                # possible_keys = [
                #     'actual_streetType', 'actual_apartmentsNum_extendedstatus', 'actual_apartmentsNum', 'country',
                #     'actual_country', 'previous_middlename', 'lastname', 'sameRegLivingAddress',
                #     'housePartNum_extendedstatus', 'actual_district', 'actual_street', 'postType',
                #     'actual_housePartNum_extendedstatus', 'previous_lastname', 'apartmentsNum_extendedstatus',
                #     'changedName', 'passport_extendedstatus', 'middlename', 'previous_middlename_extendedstatus',
                #     'streetType', 'actual_street_extendedstatus', 'public_person', 'district', 'actual_region',
                #     'actual_houseNum', 'ukr_actualAddress', 'actual_houseNum_extendedstatus', 'street',
                #     'actual_housePartNum', 'actual_cityType', 'unzr_extendedstatus', 'unzr', 'apartmentsNum',
                #     'workPlace', 'firstname', 'cityType', 'actual_buildType', 'houseNum', 'actual_postCode',
                #     'housePartNum', 'actual_cityPath', 'previous_firstname', 'actual_city', 'cityPath', 'postCategory',
                #     'region', 'passport', 'city', 'postType_extendedstatus', 'postCode', 'birthday', 'buildType',
                #     'workPost', 'taxNumber', 'houseNum_extendedstatus', 'city_extendedstatus', 'responsiblePosition',
                #     'public_person_extendedstatus', 'actual_streetType_extendedstatus', 'eng_actualPostCode',
                #     'corruptionAffected', 'eng_actualAddress', 'streetType_extendedstatus',
                #     'postCategory_extendedstatus'
                # ]
                declaration.last_employer = detailed_declaration_data['step_1']['data'].get('workPlace')
                city_of_registration_data = detailed_declaration_data['step_1']['data'].get('cityType')
                if city_of_registration_data:
                    city_of_registration = self.find_city(city_of_registration_data)
                else:
                    city_of_registration = None
                declaration.city_of_registration = city_of_registration
                # TODO: make a method for extracting residence data
                # TODO: investigate the date of birth data
                declaration.last_job_title = detailed_declaration_data['step_1']['data'].get('workPost')
                declaration.save()

                # 'Step_2' - declarant`s family
                if (
                        not declaration.spouse
                        and detailed_declaration_data['step_2']
                        and not detailed_declaration_data['step_2'].get('isNotApplicable')
                ):
                    self.save_spouse(detailed_declaration_data['step_2']['data'], pep, declaration)

                # 'Step_3' - declarant`s family`s properties
                if (detailed_declaration_data['step_3']
                        and not detailed_declaration_data['step_3'].get('isNotApplicable')):
                    self.save_property(detailed_declaration_data['step_3']['data'], declaration)
