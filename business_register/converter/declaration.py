import logging

import requests
from django.conf import settings

from business_register.converter.business_converter import BusinessConverter
from business_register.models.declaration_models import (Declaration,
                                                         Property,
                                                         PropertyRight)
from business_register.models.pep_models import Pep, RelatedPersonsLink
from location_register.models.address_models import Country
from business_register.models.company_models import Company
from data_ocean.utils import simple_format_date_to_yymmdd
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
        self.NO_DATA = {None, '[Не застосовується]', '[Не відомо]', "[Член сім'ї не надав інформацію]", }
        self.keys = set()

    def save_luxuries(self, luxuries_data, declaration):
        pass

    # TODO: implement as save_property()
    def save_unfinished_construction(self, unfinished_construction_data, declaration):
        pass

    # possible_keys = [
    #     {'ua_sameRegLivingAddress', 'percent-ownership', 'ua_regAddressFull', 'otherOwnership', 'citizen',
    #      'ua_birthday_extendedstatus', 'ua_lastname', 'ua_taxNumber_extendedstatus', 'ua_livingAddressFull',
    #      'ua_birthday', 'ownershipType', 'ua_taxNumber', 'ua_regAddressFull_extendedstatus',
    #      'percent-ownership_extendedstatus', 'seller', 'ua_middlename', 'rightBelongs', 'ua_company_code',
    #      'ua_company_name', 'ua_firstname', 'ua_livingAddressFull_extendedstatus', 'rights_id'}
    # ]
    def save_property_right(self, property, acquisition_date, rights_data, declaration):
        TYPES = {
            'Власність': PropertyRight.OWNERSHIP,
            'Спільна власність': PropertyRight.JOINT_OWNERSHIP,
            'Спільна сумісна власність': PropertyRight.COMMON_PROPERTY,
            'Оренда': PropertyRight.RENT,
            'Інше право користування': PropertyRight.OTHER_USAGE_RIGHT,
            'Власником є третя особа': PropertyRight.OWNER_IS_ANOTHER_PERSON,
            ('Право власності третьої особи, але наявні ознаки відповідно до частини 3 статті 46 '
             'ЗУ «Про запобігання корупції»'): PropertyRight.BENEFICIAL_OWNERSHIP,
            "[Член сім'ї не надав інформацію]": PropertyRight.NO_INFO_FROM_FAMILY_MEMBER,
        }
        ENIGMA = ['1', 'j', 'Інша особа (фізична або юридична)']
        for data in rights_data:
            type = TYPES.get(data.get('ownershipType'))
            share = data.get('percent-ownership')
            if share not in self.NO_DATA:
                share = float(share.replace(',', '.'))
            else:
                share = None
            owner_info = data.get('rightBelongs')
            pep = None
            # TODO: store value from ENIGMA
            if owner_info not in self.NO_DATA and owner_info not in ENIGMA:
                pep = Pep.objects.filter(nacp_id=int(owner_info)).first()
            other_owner_info = data.get('rights_id')
            if not pep and other_owner_info and other_owner_info not in ENIGMA:
                pep = Pep.objects.filter(nacp_id=int(other_owner_info)).first()
            additional_info = data.get('otherOwnership', '')
            country_of_citizenship_info = data.get('citizen')
            # TODO: return country
            country_of_citizenship = self.find_country(country_of_citizenship_info, declaration)
            last_name = data.get('ua_lastname')
            first_name = data.get('ua_firstname')
            middle_name = data.get('ua_middlename')
            if (
                    last_name not in self.NO_DATA
                    or first_name not in self.NO_DATA
                    or middle_name not in self.NO_DATA
            ):
                full_name = f'{last_name} {first_name} {middle_name}'
            else:
                full_name = ''
            if len(full_name) > 75:
                print(full_name)
            # TODO: check if taxpayer_number can have a value
            taxpayer_number = data.get('ua_taxNumber')
            if taxpayer_number and taxpayer_number != '[Конфіденційна інформація]':
                print(taxpayer_number)
            company = None
            company_code = data.get('ua_company_code')
            if company_code and company_code not in ENIGMA:
                company = Company.objects.filter(edrpou=company_code).first()
            # TODO: store 'seller', check if this field is only for changes
            # Possible values = ['Продавець']
            seller = data.get('seller')
            if seller:
                print(seller)
            PropertyRight.objects.create(
                property=property,
                type=type,
                additional_info=additional_info,
                acquisition_date=acquisition_date,
                share=share,
                pep=pep,
                company=company,
                # TODO: decide should we use lower() for storing names
                full_name=full_name,
                country_of_citizenship=country_of_citizenship
            )

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
        for data in property_data:
            property_type = TYPES.get(data['objectType'])
            if property_type == Property.OTHER:
                property_additional_info = data.get('otherObjectType')
            else:
                property_additional_info = ''
            # TODO: add country
            property_country = self.find_country(data['country'], declaration)
            property_city = None
            property_location = data.get('ua_cityType')
            # TODO: add property_city
            # if property_location:
            #     property_city = self.find_city(property_location, declaration)
            property_valuation = data.get('costAssessment')
            if property_valuation in self.NO_DATA:
                # In 2015 there was a separate field 'costDate' or 'cost_date_assessment' with the
                # valuation at the date of acquisition. Now all fields are united
                property_valuation = data.get('costDate')
                if property_valuation in self.NO_DATA:
                    property_valuation = data.get('cost_date_assessment')
            if property_valuation not in self.NO_DATA:
                property_valuation = int(property_valuation)
            else:
                property_valuation = None
            property_area = data.get('totalArea')
            if property_area not in self.NO_DATA:
                property_area = float(property_area.replace(',', '.'))
            else:
                property_area = None
            acquisition_date = simple_format_date_to_yymmdd(data.get('owningDate'))
            property = Property.objects.create(
                declaration=declaration,
                type=property_type,
                additional_info=property_additional_info,
                area=property_area,
                # country=property_country,
                # city=property_city,
                valuation=property_valuation,

            )
            # TODO: store 'sources', 'person'
            sources = data.get('sources')
            person = data.get('person')
            rights_data = data.get('rights')
            if rights_data:
                self.save_property_right(property, acquisition_date, rights_data, declaration)

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
    def save_declarant_data(self, declarant_data, pep, declaration):
        declaration.last_employer = declarant_data.get('workPlace')
        city_of_registration_data = declarant_data.get('cityType')
        if city_of_registration_data:
            city_of_registration = self.find_city(city_of_registration_data, declaration)
        else:
            city_of_registration = None
        declaration.city_of_registration = city_of_registration
        # TODO: make a method for extracting residence data
        # TODO: investigate the date of birth data
        declaration.last_job_title = declarant_data.get('workPost')
        declaration.save()

    def save_declaration(self):
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
                declaration_type = declaration_data['declaration_type']
                # TODO: predict storing changes from the declarant
                if declaration_type not in [1, 2, 3, 4]:
                    continue
                declaration_id = declaration_data['id']
                declaration = self.all_declarations.get(declaration_id)
                if declaration:
                    continue
                else:
                    declaration = Declaration.objects.create(
                        type=declaration_type,
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
                # self.save_declarant_data(detailed_declaration_data['step_1']['data'], pep, declaration)

                # # 'Step_2' - declarant`s family
                # if (
                #         not declaration.spouse
                #         and detailed_declaration_data['step_2']
                #         and not detailed_declaration_data['step_2'].get('isNotApplicable')
                # ):
                #     self.save_spouse(detailed_declaration_data['step_2']['data'], pep, declaration)

                # 'Step_3' - declarant`s family`s properties
                # if (detailed_declaration_data['step_3']
                #         and not detailed_declaration_data['step_3'].get('isNotApplicable')):
                #     self.save_property(detailed_declaration_data['step_3']['data'], declaration)

                # 'Step_4' - declarant`s family`s unfinished construction
                # if (detailed_declaration_data['step_4']
                #         and not detailed_declaration_data['step_4'].get('isNotApplicable')):
                #     self.save_unfinished_construction(detailed_declaration_data['step_4']['data'], declaration)

                # 'Step_5' - declarant`s family`s unfinished construction
                if (detailed_declaration_data['step_5']
                        and not detailed_declaration_data['step_5'].get('isNotApplicable')):
                    self.save_luxuries(detailed_declaration_data['step_5']['data'], declaration)
