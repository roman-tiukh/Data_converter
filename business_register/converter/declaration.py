import logging

from dateutil.parser import isoparse
import requests
from django.conf import settings

from business_register.converter.business_converter import BusinessConverter
from business_register.models.declaration_models import (Declaration,
                                                         Property,
                                                         PropertyRight,
                                                         LuxuryItem,
                                                         LuxuryItemRight,
                                                         Vehicle,
                                                         VehicleRight,
                                                         Securities,
                                                         SecuritiesRight,
                                                         Income,
                                                         Money,
                                                         PartTimeJob,
                                                         NgoParticipation,
                                                         Liability
                                                         )
from business_register.models.pep_models import Pep, RelatedPersonsLink
from location_register.models.address_models import Country
from business_register.models.company_models import Company
from data_ocean.utils import simple_format_date_to_yymmdd
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity

from business_register.management.commands.fetch_peps_nacp_id import is_same_full_name, InvalidRelativeData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DeclarationConverter(BusinessConverter):

    def __init__(self):
        self.only_peps = {pep.nacp_id[0]: pep for pep in Pep.objects.filter(
            is_pep=True,
            nacp_id__len=1
        )}
        self.all_declarations = self.put_objects_to_dict(
            'nacp_declaration_id',
            'business_register',
            'Declaration'
        )
        self.NO_DATA = {
            None,
            '',
            '[Не застосовується]',
            '[Не відомо]',
            "[Член сім'ї не надав інформацію]",
            '[Конфіденційна інформація]',
            'Не визначено',
            'невідомо',
        }
        self.BOOLEAN_VALUES = {
            '1': True,
            '0': False,
            "Майно набуто ДО ПОЧАТКУ ПЕРІОДУ здійснення суб'єктом декларування діяльності із "
            "виконання функцій держави або місцевого самоврядування": True,
            "Майно набуто У ПЕРІОД здійснення суб'єктом декларування діяльності із виконання "
            "функцій держави або місцевого самоврядування": False,
        }
        self.ENIGMA = {'1', 'j'}
        self.DECLARANT = '1'
        self.OTHER_PERSON = 'j'
        self.keys = set()
        self.current_declaration = None
        self.relatives_data = None

    def log_error(self, message):
        logger.error(f'Declaration id {self.current_declaration.nacp_declaration_id} : {message}')

    # TODO: decide what to do if more than one person has the same nacp_id
    def find_person(self, pep_id):
        peps = list(Pep.objects.filter(nacp_id__contains=[int(pep_id)]))
        if len(peps) == 1:
            return peps[0]
        elif len(peps) > 1:
            if self.relatives_data:
                for pep in peps:
                    for relative_data in self.relatives_data:
                        if is_same_full_name(relative_data, pep):
                            return pep
                self.log_error(f'Cannot find person with nacp_id {pep_id}. Check relatives_data {self.relatives_data}')
            else:
                self.log_error(f'empty relatives_data {self.relatives_data}')
        else:
            self.log_error(f'Cannot find person with nacp_id {pep_id}')
        return None

    def create_ngo_participation(self, data, participation_type, declaration):
        ngo_types = {
            'Саморегулівне чи самоврядне професійне об’єднання': NgoParticipation.PROFESSIONAL_UNION,
            'Громадське об’єднання': NgoParticipation.PUBLIC_ASSOCIATION,
            'Благодійна організація': NgoParticipation.CHARITY
        }
        body_types = {
            'Ревізійні органи': NgoParticipation.AUDIT_BODY,
            'Наглядові органи': NgoParticipation.SUPERVISORY_BODY,
            'Керівні органи': NgoParticipation.GOVERNING_BODY
        }

        ngo_type = ngo_types.get(data.get('objectType'))
        ngo_name = data.get('objectName')
        ngo_body_name = data.get('unitName')
        if not ngo_body_name:
            ngo_body_name = ''
        ngo_body_type = body_types.get(data.get('unitType'))
        ngo_registration_number = data.get('reestrCode')
        ngo = None
        if ngo_registration_number not in self.NO_DATA:
            ngo = Company.objects.filter(
                edrpou=ngo_registration_number,
                source=Company.UKRAINE_REGISTER
            ).first()
            if not ngo:
                self.log_error(
                    f'Cannot identify ukrainian NGO with edrpou {ngo_registration_number}.'
                    f'Check NGO data({data})'
                )
        else:
            ngo_registration_number = ''
        NgoParticipation.objects.create(
            declaration=declaration,
            participation_type=participation_type,
            ngo_type=ngo_type,
            ngo_name=ngo_name,
            ngo_registration_number=ngo_registration_number,
            ngo_body_type=ngo_body_type,
            ngo_body_name=ngo_body_name,
            ngo=ngo,
            pep=declaration.pep
        )

    def save_ngo_participation(self, ngo_data, declaration):
        # possible_keys = {'iteration', 'objectType', 'subObjectType', 'objectName', 'reestrCode'}
        membership_data = ngo_data.get('org')
        if membership_data:
            for data in membership_data:
                self.create_ngo_participation(data, NgoParticipation.MEMBERSHIP, declaration)

        # possible_keys = {'iteration', 'unitType', 'objectType', 'unitName', 'objectName', 'reestrCode'}
        leadership_data = ngo_data.get('part_org')
        if leadership_data:
            for data in leadership_data:
                self.create_ngo_participation(data, NgoParticipation.LEADERSHIP, declaration)

    # possible_keys = {
    #     'emitent_ukr_company_address', 'paid', 'emitent_ua_company_code_extendedstatus',
    #     'emitent_eng_company_code_extendedstatus', 'emitent_ua_company_code', 'iteration',
    #     'emitent_eng_company_address', 'emitent_ukr_company_name', 'description', 'emitent_eng_company_code',
    #     'emitent_ukr_company_name_extendedstatus', 'emitent_citizen', 'emitent_ua_company_name',
    #     'emitent_eng_company_address_extendedstatus', 'emitent_eng_company_name', 'margin-emitent',
    #     'emitent_ua_firstname', 'emitent_ua_lastname', 'emitent_ua_middlename'
    # }

    def save_part_time_job(self, part_time_job_data, declaration):
        is_paid_booleans = {'Оплачувана': True, 'Не оплачувана': False}
        for data in part_time_job_data:
            is_paid = is_paid_booleans.get(data.get('paid'))
            description = data.get('description', '')
            employer_from_info = data.get('emitent_citizen', '')
            employer_name = data.get('emitent_ua_company_name')
            if employer_name in self.NO_DATA:
                employer_name = data.get('emitent_ukr_company_name')
            if employer_name in self.NO_DATA:
                employer_name = ''
            employer_name_eng = data.get('emitent_eng_company_name')
            if employer_name_eng in self.NO_DATA:
                employer_name_eng = ''
            employer_address = data.get('emitent_ukr_company_address')
            if employer_address in self.NO_DATA:
                employer_address = data.get('emitent_eng_company_address')
            if employer_address in self.NO_DATA:
                employer_address = ''
            employer = None
            employer_registration_number = data.get('emitent_ua_company_code')
            if employer_registration_number not in self.NO_DATA:
                employer_registration_number = employer_registration_number.zfill(8)
                employer = Company.objects.filter(
                    edrpou=employer_registration_number,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if not employer:
                    self.log_error(
                        f'Cannot identify ukrainian company with edrpou {employer_registration_number}.'
                        f'Check part-time job data({data})'
                    )
            else:
                employer_registration_number = ''
            employer_foreign_registration_number = data.get('emitent_eng_company_code')
            if employer_foreign_registration_number not in self.NO_DATA:
                employer = Company.objects.create(
                    name=employer_name_eng,
                    edrpou=employer_foreign_registration_number,
                    address=employer_address,
                    source=Company.DECLARATIONS
                )
                employer_registration_number = employer_foreign_registration_number

            employer_last_name = data.get('emitent_ua_lastname')
            employer_first_name = data.get('emitent_ua_firstname')
            employer_middle_name = data.get('emitent_ua_middlename')
            employer_full_name = ''
            if employer_last_name and employer_first_name:
                employer_full_name = f'{employer_last_name} {employer_first_name}'
                if employer_middle_name:
                    employer_full_name = f'{employer_full_name} {employer_middle_name}'

            PartTimeJob.objects.create(
                declaration=declaration,
                is_paid=is_paid,
                description=description,
                employer_from_info=employer_from_info,
                employer_name=employer_name,
                employer_name_eng=employer_name_eng,
                employer_address=employer_address,
                employer_registration_number=employer_registration_number,
                employer=employer,
                employer_full_name=employer_full_name
            )

    possible_keys = {
        'emitent_ua_company_code_extendedstatus', 'emitent_ua_company_code', 'guarantor_realty',
        'emitent_ua_actualAddress', 'emitent_eng_regAddress', 'emitent_eng_birthday', 'emitent_eng_company_name',
        'emitent_ukr_fullname', 'dateOrigin', 'otherObjectType', 'emitent_ua_birthday_extendedstatus',
        'emitent_ukr_regAddress_extendedstatus', 'person', 'otherObjectType_extendedstatus',
        'emitent_eng_company_address', 'emitent_ukr_company_address', 'emitent_ua_middlename',
        'emitent_eng_taxNumber_extendedstatus', 'iteration', 'dateOrigin_extendedstatus', 'guarantor',
        'emitent_ukr_company_address_extendedstatus', 'sizeObligation_extendedstatus', 'emitent_ua_birthday',
        'margin-emitent_extendedstatus', 'emitent_eng_company_code', 'credit_rest_extendedstatus',
        'currency_extendedstatus', 'emitent_ua_taxNumber', 'credit_percent_paid_extendedstatus', 'person_who_care',
        'emitent_ua_middlename_extendedstatus', 'margin-emitent', 'emitent_eng_company_code_extendedstatus',
        'guarantor_realty_exist_', 'emitent_ua_sameRegLivingAddress', 'emitent_eng_company_address_extendedstatus',
        'emitent_ua_lastname', 'credit_paid', 'emitent_ukr_company_name', 'emitent_ua_firstname', 'currency',
        'sizeObligation', 'guarantor_exist_', 'emitent_ua_taxNumber_extendedstatus',
        'emitent_ua_regAddress_extendedstatus', 'emitent_eng_fullname', 'credit_paid_extendedstatus',
        'emitent_eng_birthday_extendedstatus', 'emitent_citizen', 'emitent_ukr_regAddress', 'credit_rest',
        'credit_percent_paid', 'emitent_ua_company_name', 'emitent_ua_regAddress', 'emitent_eng_taxNumber',
        'emitent_ua_actualAddress_extendedstatus', 'emitent_eng_regAddress_extendedstatus', 'objectType'
    }

    def save_liability(self, liabilities_data, declaration):
        types = {
            'Отримані кредити': Liability.LOAN,
            'Отримані позики': Liability.LOAN,
            'Розмір сплачених коштів в рахунок процентів за позикою (кредитом)':
                Liability.INTEREST_LOAN_PAYMENTS,
            'Розмір сплачених коштів в рахунок основної суми позики (кредиту)':
                Liability.LOAN_PAYMENTS,
            "Несплачені податкові зобов'язання": Liability.TAX_DEBT,
            "Зобов'язання за договорами страхування": Liability.INSURANCE,
            "Зобов'язання за договорами недержавного пенсійного забезпечення":
                Liability.PENSION_INSURANCE,
            "Зобов'язання за договорами лізингу": Liability.LEASING,
            "Кошти, позичені суб'єкту декларування або члену його сім'ї іншими особами":
                Liability.BORROWED_MONEY_BY_ANOTHER_PERSON,
            'Інше': Liability.OTHER
        }

        for data in liabilities_data:
            liability_type = types.get(data.get('objectType'))
            # TODO: check if we should store more fields when liability_type==TAX_DEBT
            additional_info = data.get('otherObjectType', '')
            currency = data.get('currency', '')
            amount = data.get('sizeObligation')
            if amount not in self.NO_DATA:
                amount = float(amount)
            loan_rest = data.get('credit_rest')
            if loan_rest not in self.NO_DATA:
                loan_rest = float(loan_rest)
            else:
                loan_rest = None
            loan_paid = data.get('credit_paid')
            if loan_paid not in self.NO_DATA:
                loan_paid = float(loan_paid)
            else:
                loan_paid = None
            interest_paid = data.get('credit_percent_paid')
            if interest_paid not in self.NO_DATA:
                interest_paid = float(interest_paid)
            else:
                interest_paid = None

            date = simple_format_date_to_yymmdd(data.get('dateOrigin'))

            bank_from_info = data.get('emitent_citizen', '')
            bank_name = data.get('emitent_ua_company_name')
            if bank_name in self.NO_DATA:
                bank_name = data.get('emitent_ukr_company_name')
            if bank_name in self.NO_DATA:
                bank_name = ''
            bank_name_eng = data.get('emitent_eng_company_name')
            if bank_name_eng in self.NO_DATA:
                bank_name_eng = ''
            bank_address = data.get('emitent_ukr_company_address')
            if bank_address in self.NO_DATA:
                bank_address = data.get('emitent_eng_company_address')
            if bank_address in self.NO_DATA:
                bank_address = ''
            bank = None
            bank_registration_number = data.get('emitent_ua_company_code')
            if bank_registration_number not in self.NO_DATA:
                bank = Company.objects.filter(
                    edrpou=bank_registration_number,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if not bank:
                    self.log_error(
                        f'Cannot identify ukrainian company with edrpou {bank_registration_number}.'
                        f'Check liability data({data})'
                    )
                    continue
            else:
                bank_registration_number = ''
            bank_foreign_registration_number = data.get('emitent_eng_company_code')
            if bank_foreign_registration_number not in self.NO_DATA:
                bank = Company.objects.create(
                    name=bank_name_eng,
                    edrpou=bank_foreign_registration_number,
                    address=bank_address,
                    source=Company.DECLARATIONS
                )
                bank_registration_number = bank_foreign_registration_number

            guarantee = ''
            guarantee_amount = None
            guarantee_registration = None
            if data.get('guarantor_realty') not in self.NO_DATA:
                # An example of this field:
                # 'guarantor_realty': [
                #     {'realty_objectType': 'Автомобіль легковий', 'realty_ua_postCode': '[Конфіденційна інформація]',
                #      'realty_ua_cityPath': '1.2.80', 'realty_ua_apartmentsNum': '[Конфіденційна інформація]',
                #      'realty_ua_housePartNum_extendedstatus': '1', 'realty_ua_streetType': '[Конфіденційна інформація]',
                #      'realty_ua_cityType': 'Київ / Україна', 'realty_ua_housePartNum': '[Конфіденційна інформація]',
                #      'realty_ua_street': '[Конфіденційна інформація]', 'region': '[Конфіденційна інформація]',
                #      'realty_cost': '931410', 'realty_country': '1',
                #      'realty_ua_houseNum': '[Конфіденційна інформація]'}]
                guarantee_info = data.get('guarantor_realty')[0]
                guarantee = guarantee_info.get('realty_objectType', '')
                guarantee_amount = guarantee_info.get('realty_cost')
                if guarantee_amount not in self.NO_DATA:
                    guarantee_amount = float(guarantee_amount)
                guarantee_registration = self.find_city(guarantee_info.get('realty_ua_cityType'))

            creditor_from_info = data.get('emitent_citizen', '')
            creditor_full_name = data.get('emitent_ukr_fullname', '')
            creditor_full_name_eng = data.get('emitent_eng_fullname', '')

            creditor_last_name = data.get('emitent_ua_lastname')
            creditor_first_name = data.get('emitent_ua_firstname')
            creditor_middle_name = data.get('emitent_ua_middlename')
            if creditor_last_name and creditor_first_name:
                creditor_full_name = f'{creditor_last_name} {creditor_first_name}'
                if creditor_middle_name:
                    creditor_full_name = f'{creditor_full_name} {creditor_middle_name}'

            owner = None
            owner_id = data.get('person')
            if owner_id in self.NO_DATA:
                owner_info = data.get('person_who_care')
                if owner_info:
                    owner_id = owner_info[0].get('person')
            if owner_id not in self.NO_DATA:
                if owner_id in self.ENIGMA:
                    owner = declaration.pep
                else:
                    owner = Pep.objects.filter(nacp_id=int(owner_id)).first()
            if not owner:
                self.log_error(f'Cannot identify owner of the liability from data({data})')
            else:
                Liability.objects.create(
                    declaration=declaration,
                    type=liability_type,
                    additional_info=additional_info,
                    amount=amount,
                    loan_rest=loan_rest,
                    loan_paid=loan_paid,
                    interest_paid=interest_paid,
                    currency=currency,
                    date=date,
                    bank_from_info=bank_from_info,
                    bank_name=bank_name,
                    bank_name_eng=bank_name_eng,
                    bank_address=bank_address,
                    bank_registration_number=bank_registration_number,
                    bank=bank,
                    guarantee=guarantee,
                    guarantee_amount=guarantee_amount,
                    guarantee_registration=guarantee_registration,
                    creditor_from_info=creditor_from_info,
                    creditor_full_name=creditor_full_name,
                    creditor_full_name_eng=creditor_full_name_eng,
                    owner=owner)

    # TODO: discover what are 'guarantor' and 'margin-emitent' (can be 'j') fields
    # looks like data starts with 'debtor_ua' is the data of the owner of the Money.Cash
    # possible_keys = {
    #     'debtor_ua_birthday', 'iteration', 'organization_eng_company_name_extendedstatus', 'debtor_ua_lastname',
    #     'debtor_ua_regAddress_extendedstatus', 'organization_type1_extendedstatus', 'debtor_ua_regAddress',
    #     'objectType', 'organization_ua_company_code', 'organization_type2', 'debtor_ua_sameRegLivingAddress',
    #     'organization_eng_company_name', 'organization_ua_company_name', 'debtor_ua_middlename',
    #     'organization_eng_company_code_extendedstatus', 'debtor_ua_taxNumber_extendedstatus',
    #     'organization_ukr_company_name', 'organization_type1', 'debtor_ua_actualAddress_extendedstatus',
    #     'debtor_ua_lastname_extendedstatus', 'organization_eng_company_code', 'organization_extendedstatus',
    #     'debtor_ua_firstname_extendedstatus', 'sizeAssets', 'debtor_ua_firstname', 'sizeAssets_extendedstatus',
    #     'rights', 'organization_eng_company_address', 'organization_ukr_company_address',
    #     'assetsCurrency_extendedstatus', 'otherObjectType', 'organization_ua_company_name_extendedstatus',
    #     'otherObjectType_extendedstatus', 'debtor_ua_actualAddress', 'person',
    #     'organization_ukr_company_address_extendedstatus', 'assetsCurrency',
    #     'organization_ukr_company_name_extendedstatus', 'debtor_ua_birthday_extendedstatus',
    #     'debtor_ua_middlename_extendedstatus', 'organization_ua_company_code_extendedstatus', 'organization',
    #     'organization_type2_extendedstatus', 'debtor_ua_taxNumber', 'organization_type',
    #     'organization_eng_company_address_extendedstatus'
    # }
    def save_money(self, money_data, declaration):
        types = {
            'Готівкові кошти': Money.CASH,
            'Кошти, розміщені на банківських рахунках': Money.BANK_ACCOUNT,
            'Внески до кредитних спілок та інших небанківських фінансових установ': Money.CONTRIBUTION,
            'Кошти, позичені третім особам': Money.LENT_MONEY,
            'Активи у дорогоцінних (банківських) металах': Money.PRECIOUS_METALS,
            'Інше': Money.OTHER
        }
        # currencies = {
        # }

        for data in money_data:
            money_type = types.get(data.get('objectType'))
            additional_info = data.get('otherObjectType', '')
            amount = data.get('sizeAssets')
            if amount not in self.NO_DATA:
                amount = float(amount)
            else:
                amount = None
            # TODO: check records after storing
            currency = data.get('assetsCurrency', '')

            if money_type in [
                Money.BANK_ACCOUNT,
                Money.CONTRIBUTION,
                Money.OTHER
            ]:
                bank_from_info = data.get('organization_type', '')
                bank_name = data.get('organization_ua_company_name')
                if bank_name in self.NO_DATA:
                    bank_name = data.get('organization_ukr_company_name')
                if bank_name in self.NO_DATA:
                    bank_name = ''
                bank_name_eng = data.get('organization_eng_company_name')
                if bank_name_eng in self.NO_DATA:
                    bank_name_eng = ''
                bank_address = data.get('organization_ukr_company_address')
                if bank_address in self.NO_DATA:
                    bank_address = data.get('organization_eng_company_address')
                if bank_address in self.NO_DATA:
                    bank_address = ''
                bank = None
                bank_registration_number = data.get('organization_ua_company_code')
                if bank_registration_number not in self.NO_DATA:
                    bank = Company.objects.filter(
                        edrpou=bank_registration_number,
                        source=Company.UKRAINE_REGISTER
                    ).first()
                    if not bank:
                        self.log_error(
                            f'Cannot identify ukrainian company with edrpou {bank_registration_number}.'
                            f'Check money data({data})'
                        )
                        continue
                else:
                    bank_registration_number = ''
                bank_foreign_registration_number = data.get('organization_eng_company_code')
                if bank_foreign_registration_number not in self.NO_DATA:
                    bank = Company.objects.create(
                        name=bank_name_eng,
                        edrpou=bank_foreign_registration_number,
                        address=bank_address,
                        source=Company.DECLARATIONS
                    )
                    bank_registration_number = bank_foreign_registration_number

            # for faster assigning, if money_type == Money.LENT_MONEY or Money.CASH:
            else:
                bank_from_info = ''
                bank_name = ''
                bank_name_eng = ''
                bank_address = ''
                bank_registration_number = ''
                bank = None

            owner = None
            owner_id = data.get('person')
            if owner_id in self.NO_DATA:
                owner_info = data.get('rights')
                if owner_info:
                    for info in owner_info:
                        owner_id = info.get('rightBelongs')
            if owner_id not in self.NO_DATA:
                if owner_id in self.ENIGMA:
                    owner = declaration.pep
                else:
                    owner = self.find_person(owner_id)
            if not owner:
                self.log_error(f'Cannot identify owner of the money from data({data})')

            else:
                Money.objects.create(
                    declaration=declaration,
                    type=money_type,
                    additional_info=additional_info,
                    amount=amount,
                    currency=currency,
                    bank_from_info=bank_from_info,
                    bank_name=bank_name,
                    bank_name_eng=bank_name_eng,
                    bank_address=bank_address,
                    bank_registration_number=bank_registration_number,
                    bank=bank,
                    owner=owner
                )

    # possible_keys = {
    #     'source_eng_company_code', 'source_ukr_regAddress', 'incomeSource', 'source_ukr_fullname', 'source_citizen',
    #     'source_ua_taxNumber', 'source_ua_actualAddress', 'source_ukr_middlename', 'sizeIncome_extendedstatus',
    #     'source_ua_middlename_extendedstatus', 'source_eng_regAddress_extendedstatus', 'otherObjectType',
    #     'source_eng_company_name_extendedstatus', 'source_ua_lastname_extendedstatus', 'source_ua_company_code',
    #     'source_ua_taxNumber_extendedstatus', 'source_ua_company_name', 'source_ua_middlename', 'source_eng_birthday',
    #     'rights', 'source_ukr_company_address_extendedstatus', 'source_ua_regAddress_extendedstatus',
    #     'source_ukr_company_name_extendedstatus', 'source_eng_company_address', 'objectType_extendedstatus',
    #     'source_ukr_company_address', 'source_eng_fullname', 'objectType', 'source_eng_sameRegLivingAddress',
    #     'source_ua_actualAddress_extendedstatus', 'source_eng_middlename', 'source_ua_birthday',
    #     'source_eng_birthday_extendedstatus', 'source_eng_lastname', 'iteration', 'source_ua_firstname',
    #     'person_who_care', 'source_eng_taxNumber_extendedstatus', 'source_ua_sameRegLivingAddress',
    #     'source_eng_company_code_extendedstatus', 'source_eng_company_address_extendedstatus',
    #     'source_ua_company_name_extendedstatus', 'source_eng_taxNumber', 'source_eng_fullname_extendedstatus',
    #     'sizeIncome', 'otherObjectType_extendedstatus', 'source_eng_firstname', 'source_ua_lastname',
    #     'source_ukr_lastname', 'incomeSource_extendedstatus', 'source_ua_firstname_extendedstatus',
    #     'source_eng_regAddress', 'source_ukr_fullname_extendedstatus', 'source_eng_company_name',
    #     'source_ua_regAddress', 'source_ua_company_code_extendedstatus', 'source_ukr_regAddress_extendedstatus',
    #     'source_ua_birthday_extendedstatus', 'source_ukr_firstname', 'source_citizen_extendedstatus',
    #     'source_ukr_company_name', 'person'
    # }
    def save_income(self, incomes_data, declaration):
        types = {
            'Дохід від зайняття підприємницькою діяльністю': Income.BUSINESS,
            'Подарунок у грошовій формі': Income.GIFT_IN_CASH,
            'Гонорари та інші виплати згідно з цивільно-правовим правочинами': Income.FEES,
            'Проценти': Income.INTEREST,
            'Дохід від надання майна в оренду': Income.RENTING_PROPERTY,
            'Пенсія': Income.PENSION,
            'Страхові виплати': Income.INSURANCE_PAYMENTS,
            'Дохід від відчуження цінних паперів та корпоративних прав': Income.SALE_OF_SECURITIES,
            'Подарунок у негрошовій формі': Income.GIFT,
            'Приз': Income.PRIZE,
            'Благодійна допомога': Income.CHARITY,
            'Дохід від відчуження нерухомого майна': Income.SALE_OF_PROPERTY,
            'Спадщина': Income.LEGACY,
            'Заробітна плата отримана за сумісництвом': Income.PART_TIME_SALARY,
            'Дохід від відчуження рухомого майна ( крім цінних паперів та корпоративних прав)':
                Income.SALE_OF_LUXURIES,
            'Дохід від відчуження рухомого майна (крім цінних паперів та корпоративних прав)':
                Income.SALE_OF_LUXURIES,
            'Заробітна плата отримана за основним місцем роботи': Income.SALARY,
            'Дохід від зайняття незалежною професійною діяльністю': Income.SELF_EMPLOYMENT,
            'Дивіденди': Income.DIVIDENDS,
            'Інше': Income.OTHER,
            'Роялті': Income.ROYALTY
        }
        for data in incomes_data:
            income_type = data.get('objectType')
            # TODO: decide what to do when value income_type == '[Член сім\'ї не надав інформацію]'
            if income_type and income_type in self.NO_DATA:
                self.log_error(f'Wrong value for type of income: income_type = {income_type}.Check income data({data})')
                continue
            else:
                income_type = types.get(data.get('objectType'))
            additional_info = data.get('otherObjectType', '')
            amount = data.get('sizeIncome')
            if amount not in self.NO_DATA:
                amount = int(amount)
            # TODO: decide what to do when value == '[Член сім\'ї не надав інформацію]'
            else:
                amount = None

            # examples of the value: 'Юридична особа, зареєстрована в Україні',
            # 'Юридична особа, зареєстрована за кордоном', 'Громадянин України'
            from_info = data.get('source_citizen', '')

            # TODO: store separately from Company object all info of the company that paid
            company = None
            company_code = data.get('source_ua_company_code')
            if company_code not in self.NO_DATA and company_code not in self.ENIGMA:
                company_code = company_code.zfill(8)
                # FIXME: If the Ukrainian company has source = antac ?
                company = Company.objects.filter(
                    edrpou=company_code,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if not company:
                    self.log_error(
                        f'Cannot identify ukrainian company with edrpou {company_code}.'
                        f'Check income data({data})'
                    )
            foreign_company_code = data.get('source_eng_company_code')
            if company_code not in self.NO_DATA and foreign_company_code not in self.ENIGMA:
                if not company:
                    # FIXME: If the same company is in a different declaration, will there be two identical companies?
                    Company.objects.create(
                        name=data.get('source_eng_company_name'),
                        edrpou=foreign_company_code,
                        address=data.get('source_eng_company_address'),
                        source=Company.DECLARATIONS
                    )

            full_name = data.get('source_ukr_fullname')
            if not full_name:
                full_name = data.get('source_eng_fullname')
            last_name = data.get('source_ua_lastname')
            if not last_name:
                last_name = data.get('source_ukr_lastname')
            if not last_name:
                last_name = data.get('source_eng_lastname')
            first_name = data.get('source_ua_firstname')
            if not first_name:
                first_name = data.get('source_ukr_firstname')
            if not first_name:
                first_name = data.get('source_eng_firstname')
            middle_name = data.get('source_ua_middlename')
            if not middle_name:
                middle_name = data.get('source_ukr_middlename')
            if not middle_name:
                middle_name = data.get('source_eng_middlename')
            if last_name and first_name:
                full_name = f'{last_name} {first_name}'
                if middle_name:
                    full_name = f'{full_name} {middle_name}'
            if not full_name:
                full_name = ''

            recipient = None
            # value could be 'j'
            recipient_code = data.get('incomeSource')
            if not recipient_code:
                recipient_code = data.get('person')
            recipient_data = data.get('person_who_care')
            if recipient_data:
                recipient_code = recipient_data[0].get('person')
            if recipient_code in self.ENIGMA:
                recipient = declaration.pep
            elif recipient_code in self.NO_DATA:
                recipient_code = ''
            elif recipient_code.isalpha():
                self.log_error(f'Wrong value for recipient_code in income: recipient_code = {recipient_code}.'
                               f'Check income data({data})')
            else:
                recipient = self.find_person(recipient_code)
            # TODO: Check if we can extract recipient from rights_data like in Money
            rights_data = data.get('rights')
            if not recipient:
                self.log_error(
                    f'Cannot identify income recipient with NACP id {recipient_code}.'
                    f'Check income data({data})'
                )
                continue

            income = Income.objects.create(
                declaration=declaration,
                type=income_type,
                additional_info=additional_info,
                amount=amount,
                paid_by_company=company,
                paid_by_person=full_name,
                from_info=from_info,
                recipient=recipient
            )

            # TODO: discover  'iteration'. Example of the value '1614443380219'
            iteration = data.get('iteration')

    # TODO: implement
    def save_securities_right(self, securities, acquisition_date, rights_data):
        pass

    # looks like data starts from 'emitent_ua_' is the owner of securities data
    # possible_keys = {
    #     'cost_extendedstatus', 'emitent_eng_fullname', 'emitent_ukr_company_address',
    #     'emitent_ua_company_name_extendedstatus', 'persons_eng_company_name', 'typeProperty',
    #     'persons_eng_company_address', 'emitent_eng_fullname_extendedstatus', 'persons_ua_company_name',
    #     'emitent_eng_company_address', 'persons_ua_birthday', 'persons_ua_actual_address_extendedstatus',
    #     'emitent_ua_sameRegLivingAddress', 'persons_ua_reg_address_extendedstatus', 'emitent_ua_taxNumber',
    #     'persons_eng_company_address_extendedstatus', 'emitent_eng_company_name', 'persons_date', 'emitent_ua_birthday',
    #     'persons_ukr_company_name', 'emitent_ua_actualAddress', 'persons_ua_reg_address', 'emitent_ua_lastname',
    #     'subTypeProperty2', 'emitent_ua_company_code_extendedstatus', 'emitent_eng_company_name_extendedstatus',
    #     'rights', 'person', 'emitent_ukr_company_name_extendedstatus', 'emitent_ukr_company_name',
    #     'persons_extendedstatus', 'emitent_type', 'emitent_ua_firstname', 'emitent_ua_company_code',
    #     'persons_ua_middlename', 'persons_ua_firstname', 'cost', 'persons_ua_actual_address',
    #     'otherObjectType_extendedstatus', 'emitent_ukr_fullname', 'emitent_ukr_company_address_extendedstatus',
    #     'emitent_ukr_fullname_extendedstatus', 'owningDate_extendedstatus', 'emitent_ua_company_name',
    #     'emitent_eng_company_code', 'emitent_ua_regAddress', 'subTypeProperty1', 'emitent_ua_middlename',
    #     'persons_ua_taxNumber', 'persons_ua_birthday_extendedstatus', 'emitent_eng_company_code_extendedstatus',
    #     'persons_ua_lastname', 'iteration', 'persons_ua_same_address', 'persons_eng_company_code', 'otherObjectType',
    #     'persons_ukr_company_address', 'persons_type', 'emitent_eng_company_address_extendedstatus', 'owningDate',
    #     'amount', 'emitent', 'persons', 'persons_date_extendedstatus', 'persons_eng_company_code_extendedstatus',
    #     'persons_ua_company_code', 'amount_extendedstatus', 'emitent_extendedstatus'
    # }
    def save_securities(self, securities_data, declaration):
        types = {
            'Іпотечні цінні папери': Securities.MORTGAGE_SECURITIES,
            'Інше': Securities.OTHER,
            'Товаророзпорядчі цінні папери': Securities.COMMODITY_SECURITIES,
            'Акції': Securities.SHARE,
            'Похідні цінні папери (деривативи)': Securities.DERIVATIVES,
            'Боргові цінні папери': Securities.DEBT_SECURITIES,
            'Приватизаційні цінні папери (ваучери тощо)': Securities.PRIVATIZATION_SECURITIES,
            'Інвестиційні сертифікати': Securities.INVESTMENT_CERTIFICATES,
            'Чеки': Securities.CHECK
        }
        # TODO: decide should we store that
        # subtype_1 = {
        #     'Облігації підприємств', "Казначейські зобов'язання", None, 'Державні облігації України',
        #     'Ощадні (депозитні) сертифікати'
        # }

        for data in securities_data:
            securities_type = types.get(data.get('typeProperty'))
            additional_info = data.get('otherObjectType', '')

            issuer_from_info = data.get('emitent_type', '')
            issuer_name = data.get('emitent_ua_company_name')
            if issuer_name in self.NO_DATA:
                issuer_name = data.get('emitent_ukr_company_name')
            if issuer_name in self.NO_DATA:
                issuer_name = ''
            issuer_name_eng = data.get('emitent_eng_company_name')
            if issuer_name_eng in self.NO_DATA:
                issuer_name_eng = ''
            issuer_address = data.get('emitent_ukr_company_address')
            if issuer_address in self.NO_DATA:
                issuer_address = data.get('emitent_eng_company_address')
            if issuer_address in self.NO_DATA:
                issuer_address = ''
            issuer = None
            issuer_registration_number = data.get('emitent_ua_company_code')
            if issuer_registration_number not in self.NO_DATA:
                issuer_registration_number = issuer_registration_number.zfill(8)
                # FIXME: If the Ukrainian company has source = 'antac' ?
                issuer = Company.objects.filter(
                    edrpou=issuer_registration_number,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if not issuer:
                    self.log_error(
                        f'Cannot identify ukrainian company with edrpou {issuer_registration_number}.'
                        f'Check income data({data})'
                    )
            else:
                issuer_registration_number = ''
            issuer_foreign_registration_number = data.get('emitent_eng_company_code')
            if issuer_foreign_registration_number not in self.NO_DATA:
                # FIXME: If the same company is in a different declaration, will there be two identical companies?
                issuer = Company.objects.create(
                    name=issuer_name_eng,
                    edrpou=issuer_foreign_registration_number,
                    address=issuer_address,
                    source=Company.DECLARATIONS
                )
                issuer_registration_number = issuer_foreign_registration_number

            # TODO: Discover what is 'emitent'
            # example of the value: 'j'
            # emitent = data.get('emitent')
            # TODO: Discover what are 'persons_date', 'person', 'persons'
            # transfer_date = data.get('persons_date')
            # person = data.get('person')
            # persons = data.get('persons')

            trustee_from_info = data.get('persons_type', '')
            trustee_name = data.get('persons_ua_company_name')
            if trustee_name in self.NO_DATA:
                trustee_name = data.get('persons_ukr_company_name')
            if trustee_name in self.NO_DATA:
                trustee_name = ''
            trustee_name_eng = data.get('persons_eng_company_name')
            if trustee_name_eng in self.NO_DATA:
                trustee_name_eng = ''
            trustee_address = data.get('persons_ukr_company_address')
            if trustee_address in self.NO_DATA:
                trustee_address = data.get('persons_eng_company_address')
            if trustee_address in self.NO_DATA:
                trustee_address = ''
            trustee_registration_number = data.get('persons_ua_company_code')
            trustee = None
            if trustee_registration_number not in self.NO_DATA:
                trustee_registration_number = trustee_registration_number.zfill(8)
                # FIXME: If the Ukrainian company has source = 'antac' ?
                trustee = Company.objects.filter(
                    edrpou=trustee_registration_number,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if not trustee:
                    self.log_error(
                        f'Cannot identify ukrainian company with edrpou {trustee_registration_number}.'
                        f'Check income data({data})'
                    )
            else:
                trustee_registration_number = ''

            trustee_foreign_registration_number = data.get('persons_eng_company_code')
            if trustee_foreign_registration_number not in self.NO_DATA:
                # FIXME: If the same company is in a different declaration, will there be two identical companies?
                trustee = Company.objects.create(
                    name=trustee_name_eng,
                    edrpou=trustee_foreign_registration_number,
                    address=trustee_address,
                    source=Company.DECLARATIONS
                )
                trustee_registration_number = trustee_foreign_registration_number

            quantity = data.get('amount')
            if quantity not in self.NO_DATA:
                quantity = int(quantity)
            else:
                quantity = None
            nominal_value = data.get('cost')
            if nominal_value not in self.NO_DATA:
                nominal_value = float(nominal_value.replace(',', '.'))
            else:
                nominal_value = None
            securities = Securities.objects.create(
                declaration=declaration,
                type=securities_type,
                additional_info=additional_info,
                issuer_from_info=issuer_from_info,
                issuer_name=issuer_name,
                issuer_name_eng=issuer_name_eng,
                issuer_address=issuer_address,
                issuer_registration_number=issuer_registration_number,
                issuer=issuer,
                trustee_from_info=trustee_from_info,
                trustee_name=trustee_name,
                trustee_name_eng=trustee_name_eng,
                trustee_address=trustee_address,
                trustee_registration_number=trustee_registration_number,
                trustee=trustee,
                quantity=quantity,
                nominal_value=nominal_value
            )

            acquisition_date = simple_format_date_to_yymmdd(data.get('owningDate'))
            rights_data = data.get('rights')
            if rights_data:
                self.save_securities_right(securities, acquisition_date, rights_data)

    # TODO: implement
    def save_vehicle_right(self, vehicle, acquisition_date, rights_data):
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
            if owner_info not in self.NO_DATA and owner_info not in self.ENIGMA:
                pep = self.find_person(owner_info)
            other_owner_info = data.get('rights_id')
            # Store value 'Інша особа (фізична або юридична)'
            if not pep and other_owner_info and other_owner_info not in self.ENIGMA:
                pep = self.find_person(owner_info)
            additional_info = data.get('otherOwnership', '')
            country_of_citizenship_info = data.get('citizen')
            # TODO: return country
            if country_of_citizenship_info:
                country_of_citizenship = self.find_country(country_of_citizenship_info)
            else:
                country_of_citizenship = None
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
            # TODO: check if taxpayer_number can have a value
            taxpayer_number = data.get('ua_taxNumber')
            if taxpayer_number and taxpayer_number != '[Конфіденційна інформація]':
                print(taxpayer_number)
            company = None
            company_code = data.get('ua_company_code')
            if company_code not in self.ENIGMA:
                company = Company.objects.filter(
                    edrpou=company_code,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if not company:
                    self.log_error(
                        f'Cannot identify ukrainian company with edrpou {company_code}.'
                        f'Check right data ({data}) to {vehicle.type}'
                    )
            VehicleRight.objects.create(
                car=vehicle,
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

    # TODO: implement
    def is_vehicle_luxury(self, brand, model, year):
        pass

    # possible_keys = {
    #     'object_identificationNumber', 'brand', 'owningDate_extendedstatus', 'model_extendedstatus',
    #     'iteration', 'model', 'object_identificationNumber_extendedstatus',
    #     'graduationYear_extendedstatus', 'person', 'objectType', 'graduationYear',
    #     'otherObjectType_extendedstatus', 'costDate_extendedstatus', 'rights', 'otherObjectType',
    #     'costDate', 'owningDate'
    # }
    def save_vehicle(self, vehicles_data, declaration):
        types = {
            'Автомобіль легковий': Vehicle.CAR,
            'Автомобіль вантажний': Vehicle.TRUCK,
            'Мотоцикл (мопед)': Vehicle.MOTORBIKE,
            'Водний засіб': Vehicle.BOAT,
            'Сільськогосподарська техніка': Vehicle.AGRICULTURAL_MACHINERY,
            'Інше': Vehicle.OTHER
        }
        for data in vehicles_data:
            vehicle_type = types.get(data.get('objectType'))
            additional_info = data.get('otherObjectType', '')
            brand = data.get('brand')
            model = data.get('model')
            year = data.get('graduationYear')
            if year in self.NO_DATA:
                year = None
            valuation = data.get('costDate')
            if valuation not in self.NO_DATA:
                valuation = int(valuation)
            else:
                valuation = None
            is_luxury = self.is_vehicle_luxury(brand, model, year)
            vehicle = Vehicle.objects.create(
                declaration=declaration,
                type=vehicle_type,
                additional_info=additional_info,
                brand=brand,
                model=model,
                year=year,
                is_luxury=is_luxury,
                valuation=valuation
            )
            acquisition_date = simple_format_date_to_yymmdd(data.get('owningDate'))
            # TODO: store  'person'
            person = data.get('person')
            rights_data = data.get('rights')
            if rights_data:
                self.save_vehicle_right(vehicle, acquisition_date, rights_data)

    # TODO: implement
    def save_luxury_right(self, luxury_item, acquisition_date, rights_data):
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
            if owner_info not in self.NO_DATA and owner_info not in self.ENIGMA:
                pep = self.find_person(owner_info)
            other_owner_info = data.get('rights_id')
            # Store value 'Інша особа (фізична або юридична)'
            if not pep and other_owner_info and other_owner_info not in self.ENIGMA:
                pep = self.find_person(other_owner_info)

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

            LuxuryItemRight.objects.create(
                luxury_item=luxury_item,
                type=type,
                acquisition_date=acquisition_date,
                share=share,
                pep=pep,
                full_name=full_name,
            )

    # possible_keys = {
    #     'otherObjectType', 'costDateUse_extendedstatus', 'dateUse', 'manufacturerName',
    #     'manufacturerName_extendedstatus', 'dateUse_extendedstatus', 'propertyDescr_extendedstatus',
    #     'acqPeriod', 'objectType', 'rights', 'trademark_extendedstatus', 'trademark', 'costDateUse',
    #     'acqBeforeFD', 'person', 'iteration', 'propertyDescr', 'otherObjectType_extendedstatus'
    # }
    def save_luxury_item(self, luxuries_data, declaration):
        types = {
            'Твір мистецтва (картина тощо)': LuxuryItem.ART,
            'Персональні або домашні електронні пристрої': LuxuryItem.ELECTRONIC_DEVICES,
            'Антикварний виріб': LuxuryItem.ANTIQUES,
            'Одяг': LuxuryItem.CLOTHES,
            'Ювелірні вироби': LuxuryItem.JEWELRY,
            'Інше': LuxuryItem.OTHER
        }
        for data in luxuries_data:
            luxury_type = types.get(data.get('objectType'))
            additional_info = data.get('otherObjectType', '')
            acquired_before_first_declaration = self.BOOLEAN_VALUES.get(data.get('acqBeforeFD'))
            acquisition_period = data.get('acqPeriod')
            if acquired_before_first_declaration is None and acquisition_period:
                acquired_before_first_declaration = self.BOOLEAN_VALUES.get(acquisition_period)
            trademark = data.get('trademark') if data.get('trademark') not in self.NO_DATA else ''
            producer = data.get('manufacturerName') if data.get('manufacturerName') not in self.NO_DATA else ''
            description = data.get('propertyDescr', '')
            valuation = data.get('costDateUse')
            if valuation not in self.NO_DATA:
                valuation = int(valuation)
            else:
                valuation = None
            luxury_item = LuxuryItem.objects.create(
                declaration=declaration,
                type=luxury_type,
                additional_info=additional_info,
                acquired_before_first_declaration=acquired_before_first_declaration,
                trademark=trademark,
                producer=producer,
                description=description,
                valuation=valuation
            )
            acquisition_date = data.get('dateUse')
            if acquisition_date:
                acquisition_date = simple_format_date_to_yymmdd(acquisition_date)
            # TODO: store  'person'
            person = data.get('person')
            rights_data = data.get('rights')
            if rights_data:
                self.save_luxury_right(luxury_item, acquisition_date, rights_data)

    # TODO: implement as save_property()
    def save_unfinished_construction(self, unfinished_construction_data, declaration):
        for data in unfinished_construction_data:
            additional_info = data.get('objectType')
            # TODO: add country
            country = self.find_country(data['country'])
            city = None
            property_location = data.get('ua_cityType')
            # TODO: add unfinished_construction_city
            if property_location:
                city = self.find_city(property_location)
            area = data.get('totalArea')
            if area not in self.NO_DATA:
                area = float(area.replace(',', '.'))
            else:
                area = None
            unfinished_construction_property = Property.objects.create(
                declaration=declaration,
                type=Property.UNFINISHED_CONSTRUCTION,
                additional_info=additional_info,
                area=area,
                country=country,
                city=city,
            )

    # possible_keys = [
    #     {'ua_sameRegLivingAddress', 'percent-ownership', 'ua_regAddressFull', 'otherOwnership', 'citizen',
    #      'ua_birthday_extendedstatus', 'ua_lastname', 'ua_taxNumber_extendedstatus', 'ua_livingAddressFull',
    #      'ua_birthday', 'ownershipType', 'ua_taxNumber', 'ua_regAddressFull_extendedstatus',
    #      'percent-ownership_extendedstatus', 'seller', 'ua_middlename', 'rightBelongs', 'ua_company_code',
    #      'ua_company_name', 'ua_firstname', 'ua_livingAddressFull_extendedstatus', 'rights_id'}
    # ]
    def save_property_right(self, property, acquisition_date, rights_data):
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
        UKRAINE_NACP_ID = '1'
        for data in rights_data:
            type = TYPES.get(data.get('ownershipType'))
            share = data.get('percent-ownership')
            if share not in self.NO_DATA:
                share = float(share.replace(',', '.'))
            else:
                share = None
            owner_id = data.get('rightBelongs')
            pep = None
            # TODO: store value from ENIGMA
            if owner_id not in self.NO_DATA:
                if owner_id == self.DECLARANT:
                    pep = property.declaration.pep
                elif owner_id == self.OTHER_PERSON:
                    # TODO: decide should we store PEP 'Власником є третя особа' and use it in such case
                    pass
                else:
                    pep = self.find_person(owner_id)
            other_owner_info = data.get('rights_id')
            if not pep and other_owner_info:
                if other_owner_info == self.DECLARANT:
                    pep = property.declaration.pep
                elif other_owner_info == self.OTHER_PERSON:
                    # TODO: decide should we store PEP 'Власником є третя особа' and use it in such case
                    pass
                else:
                    pep = self.find_person(other_owner_info)

            additional_info = data.get('otherOwnership', '')
            country_of_citizenship_info = data.get('citizen')
            # TODO: return country
            if country_of_citizenship_info:
                if country_of_citizenship_info == 'Громадянин України':
                    country_of_citizenship_info = UKRAINE_NACP_ID
                country_of_citizenship = self.find_country(country_of_citizenship_info)
            else:
                country_of_citizenship = None
            last_name = data.get('ua_lastname')
            first_name = data.get('ua_firstname')
            middle_name = data.get('ua_middlename') if data.get('ua_middlename') not in self.NO_DATA else ''
            ukr_full_name = data.get('ukr_fullname')
            eng_full_name = data.get('eng_fullname')
            if (
                    last_name not in self.NO_DATA
                    or first_name not in self.NO_DATA
                    or middle_name not in self.NO_DATA
            ):
                full_name = f'{last_name} {first_name} {middle_name}'
            elif ukr_full_name not in self.NO_DATA:
                full_name = ukr_full_name
            elif eng_full_name not in self.NO_DATA:
                full_name = eng_full_name
            else:
                full_name = ''

            company = None
            company_code = data.get('ua_company_code')
            if company_code not in self.ENIGMA and company_code not in self.NO_DATA:
                company = Company.objects.filter(
                    edrpou=company_code,
                    source=Company.UKRAINE_REGISTER
                ).first()
                if not company:
                    self.log_error(
                        f'Cannot identify ukrainian company with edrpou {company_code}.'
                        f'Check right data ({data}) to {property.type}'
                    )
            # TODO: store 'seller', check if this field is only for changes
            # Possible values = ['Продавець']
            seller = data.get('seller')

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
            if type(data['objectType']) != str:
                self.log_error(f'Invalid value: property_type = {data["objectType"]}')
                continue
            property_type = TYPES.get(data['objectType'])
            additional_info = data.get('otherObjectType', '')
            # TODO: add country
            country = self.find_country(data['country'])
            city = None
            property_location = data.get('ua_cityType')
            # TODO: add property_city
            if property_location:
                city = self.find_city(property_location)
            valuation = data.get('costAssessment')
            if valuation in self.NO_DATA:
                # In 2015 there was a separate field 'costDate' or 'cost_date_assessment' with the
                # valuation at the date of acquisition. Now all fields are united
                valuation = data.get('costDate')
                if valuation in self.NO_DATA:
                    valuation = data.get('cost_date_assessment')
            if valuation not in self.NO_DATA:
                try:
                    valuation = float(valuation.replace(',', '.'))
                except ValueError:
                    self.log_error(f'Invalid value: valuation = {valuation}')
                    valuation = None
            else:
                valuation = None
            area = data.get('totalArea')
            if area not in self.NO_DATA:
                area = float(area.replace(',', '.'))
            else:
                area = None
            acquisition_date = data.get('owningDate') if data.get('owningDate') not in self.NO_DATA else None
            if acquisition_date:
                acquisition_date = simple_format_date_to_yymmdd(acquisition_date)
                if len(acquisition_date) < 10:
                    self.log_error(f'Wrong value for acquisition_date = {acquisition_date}')
                    acquisition_date = None
            property = Property.objects.create(
                declaration=declaration,
                type=property_type,
                additional_info=additional_info,
                area=area,
                country=country,
                city=city,
                valuation=valuation,
            )
            # TODO: investigate 'sources'
            sources = data.get('sources')
            rights_data = data.get('rights')
            if rights_data:
                self.save_property_right(property, acquisition_date, rights_data)
            else:
                # TODO: decide how to store property right when there is no 'rights' field - only 'person'
                person = data.get('person')

    # TODO: retrieve country from Country DB
    def find_country(self, property_country_data):
        if property_country_data.isdigit():
            country = Country.objects.filter(nacp_id=property_country_data).first()
            if country:
                return country
            else:
                self.log_error(f'Cannot find country id {property_country_data}')
        else:
            self.log_error(f'Invalid value for country: {property_country_data}')

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
            elif 'область' in part or 'автономна республіка крим' in part:
                region = part
            elif part in city_region:
                city = region = part
            else:
                city = part
        return city, region, district

    def find_city(self, address_data):
        city, region, district = self.split_address_data(address_data)
        ratu_region = RatuRegion.objects.filter(name=region).first()
        ratu_district = RatuDistrict.objects.filter(name=district, region=ratu_region).first()
        if region and not ratu_region:
            self.log_error(f'Cannot find region {region}')
        if district and not ratu_district:
            self.log_error(f'Cannot find district {district}')
        else:
            city_of_registration = RatuCity.objects.filter(
                name=city,
                region=ratu_region,
                district=ratu_district
            ).first()
            return city_of_registration
        self.log_error(f'Cannot find city')

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
    def save_related_person(self, pep, declaration):
        SPOUSE_TYPES = ['дружина', 'чоловік']
        for relative_data in self.relatives_data:
            to_person_relationship_type = relative_data.get('subjectRelation')
            related_person_links = RelatedPersonsLink.objects.filter(
                from_person=pep,
                to_person_relationship_type=to_person_relationship_type
            )
            # TODO: decide should we store new Pep here
            for link in related_person_links:
                related_person = link.to_person
                related_person_nacp_id = relative_data.get('id')
                try:
                    if not is_same_full_name(relative_data, related_person):
                        continue
                except InvalidRelativeData as e:
                    self.log_error(f'{e}')
                    continue
                if not isinstance(related_person_nacp_id, int) or related_person_nacp_id == 0:
                    self.log_error(f'Check invalid declarant NACP id ({related_person_nacp_id})')
                elif related_person_nacp_id in related_person.nacp_id:
                    pass
                else:
                    related_person.nacp_id.append(related_person_nacp_id)
                    related_person.save()
                if to_person_relationship_type in SPOUSE_TYPES:
                    declaration.spouse = related_person
                    declaration.save()

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
        city_of_residence_data = declarant_data.get('actual_cityType')
        if city_of_registration_data:
            city_of_registration = self.find_city(city_of_registration_data)
        else:
            city_of_registration = None
        declaration.city_of_registration = city_of_registration
        # TODO: make a method for extracting residence data
        if city_of_residence_data:
            city_of_residence = self.find_city(city_of_residence_data)
        else:
            city_of_residence = None
        declaration.city_of_residence = city_of_residence
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
                # possible_keys = {
                #     'post_type', 'corruption_affected', 'id', 'options', 'type', 'declaration_type',
                #     'responsible_position', 'declaration_year', 'schema_version', 'data', 'post_category',
                #     'date', 'user_declarant_id'
                # }
                declaration_type = declaration_data['declaration_type']
                # TODO: predict storing changes from the declarant
                if declaration_type not in [1, 2, 3, 4]:
                    continue
                declaration_id = declaration_data['id']
                declaration = self.all_declarations.get(declaration_id)
                if declaration:
                    continue
                # TODO: add date to the model and here
                else:
                    submission_date = isoparse(declaration_data['date']).date()
                    declaration = Declaration.objects.create(
                        type=declaration_type,
                        year=declaration_data['declaration_year'],
                        submission_date=submission_date,
                        nacp_declaration_id=declaration_id,
                        nacp_declarant_id=nacp_declarant_id,
                        pep=pep,
                    )
                self.current_declaration = declaration

                # getting full declaration data
                response = requests.get(settings.NACP_DECLARATION_RETRIEVE + declaration_id)
                if response.status_code != 200:
                    self.log_error(f'cannot find declarations')
                    continue
                # possible_keys = {
                #     'step_9', 'step_13', 'step_3', 'step_14', 'step_16', 'step_11', 'step_17',
                #     'step_6', 'step_5', 'step_8', 'step_0', 'step_1', 'step_7', 'step_2',
                #     'step_4', 'step_12', 'step_10', 'step_15',
                # }
                detailed_declaration_data = response.json()['data']

                # TODO: predict updating
                # 'Step_1' - declarant`s personal data
                # self.save_declarant_data(detailed_declaration_data['step_1']['data'], pep, declaration)

                # TODO: predict updating
                # 'Step_2' - declarant`s family
                if (
                        not declaration.spouse
                        and detailed_declaration_data['step_2']
                        and not detailed_declaration_data['step_2'].get('isNotApplicable')
                ):
                    self.relatives_data = detailed_declaration_data['step_2']['data']
                    self.save_related_person(pep, declaration)
                else:
                    self.relatives_data = None

                # 'Step_3' - declarant`s family`s properties
                # if (detailed_declaration_data['step_3']
                #         and not detailed_declaration_data['step_3'].get('isNotApplicable')):
                #     self.save_property(detailed_declaration_data['step_3']['data'], declaration)

                # 'Step_4' - declarant`s family`s unfinished construction
                # if (detailed_declaration_data['step_4']
                #         and not detailed_declaration_data['step_4'].get('isNotApplicable')):
                #     self.save_unfinished_construction(detailed_declaration_data['step_4']['data'], declaration)

                # 'Step_5' - declarant`s family`s luxury items
                # if (detailed_declaration_data['step_5']
                #         and not detailed_declaration_data['step_5'].get('isNotApplicable')):
                #     self.save_luxury_item(detailed_declaration_data['step_5']['data'], declaration)

                # 'Step_6' - declarant`s family`s vehicles
                # if (detailed_declaration_data['step_6']
                #         and not detailed_declaration_data['step_6'].get('isNotApplicable')):
                #     self.save_vehicle(detailed_declaration_data['step_6']['data'], declaration)

                # 'Step_7' - declarant`s family`s securities
                # if (detailed_declaration_data['step_7']
                #         and not detailed_declaration_data['step_7'].get('isNotApplicable')):
                #     self.save_securities(detailed_declaration_data['step_7']['data'], declaration)

                # 'Step_8' - declarant`s family`s companies
                # if (detailed_declaration_data['step_8']
                #         and not detailed_declaration_data['step_8'].get('isNotApplicable')):
                #     self.save_companies(detailed_declaration_data['step_8']['data'], declaration)

                # 'Step_9' - companies where declarant`s family`s members are beneficiaries
                # if (detailed_declaration_data['step_9']
                #         and not detailed_declaration_data['step_9'].get('isNotApplicable')):
                #     self.save_beneficiary_of(detailed_declaration_data['step_9']['data'], declaration)

                # 'Step_11' - declarant`s family`s incomes
                # if (detailed_declaration_data['step_11']
                #         and not detailed_declaration_data['step_11'].get('isNotApplicable')):
                #     self.save_income(detailed_declaration_data['step_11']['data'], declaration)

                # 'Step_12' - declarant`s family`s money
                # if (detailed_declaration_data['step_12']
                #         and not detailed_declaration_data['step_12'].get('isNotApplicable')):
                #     self.save_money(detailed_declaration_data['step_12']['data'], declaration)

                # 'Step_13' - declarant`s family`s liabilities
                if (detailed_declaration_data['step_13']
                        and not detailed_declaration_data['step_13'].get('isNotApplicable')):
                    self.save_liability(detailed_declaration_data['step_13']['data'], declaration)

                # 'Step_15' - declarant`s part-time job info
                # if (detailed_declaration_data['step_15']
                #         and not detailed_declaration_data['step_15'].get('isNotApplicable')):
                #     self.save_part_time_job(detailed_declaration_data['step_15']['data'], declaration)

                # 'Step_16' - declarant`s membership in NGOs
                # if (detailed_declaration_data['step_16']
                #         and not detailed_declaration_data['step_16'].get('isNotApplicable')):
                #     self.save_ngo_participation(detailed_declaration_data['step_16']['data'], declaration)
