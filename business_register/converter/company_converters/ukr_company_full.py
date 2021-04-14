import codecs
import logging
import os
import re
import tempfile
from time import sleep
import requests
from django.conf import settings
from django.utils import timezone

from data_ocean.models import Authority
from business_register.converter.company_converters.company import CompanyConverter
from business_register.models.company_models import (
    Assignee, BancruptcyReadjustment, Bylaw, Company, CompanyDetail, CompanyToKved,
    CompanyToPredecessor, ExchangeDataCompany, Founder, Predecessor,
    Signer, TerminationStarted
)
from data_ocean.converter import BulkCreateManager
from data_ocean.downloader import Downloader
from data_ocean.utils import (cut_first_word, format_date_to_yymmdd, get_first_word,
                              to_lower_string_if_exists)
from location_register.converter.address import AddressConverter
from stats.tasks import endpoints_cache_warm_up

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UkrCompanyFullConverter(CompanyConverter):
    """
    Uncomment for switch Timer ON.
    """
    # timing = True

    def __init__(self):
        self.LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_FULL
        self.LOCAL_FOLDER = settings.LOCAL_FOLDER
        self.CHUNK_SIZE = settings.CHUNK_SIZE_UO_FULL
        self.RECORD_TAG = 'SUBJECT'
        self.bulk_manager = BulkCreateManager()
        self.branch_bulk_manager = BulkCreateManager()
        self.all_bylaw_dict = self.put_objects_to_dict("name", "business_register", "Bylaw")
        self.all_predecessors_dict = self.put_objects_to_dict("name", "business_register", "Predecessor")
        self.all_companies_dict = {}
        self.branch_to_parent = {}
        self.all_company_founders = []
        self.founder_to_dict = {}
        self.company_detail_to_dict = {}
        self.company_to_kved_to_dict = {}
        self.signer_to_dict = {}
        self.termination_started_to_dict = {}
        self.bancruptcy_readjustment_to_dict = {}
        self.company_to_predecessor_to_dict = {}
        self.assignee_to_dict = {}
        self.exchange_data_to_dict = {}
        self.company_country = AddressConverter().save_or_get_country('Ukraine')
        self.source = Company.UKRAINE_REGISTER
        self.already_stored_companies =\
            list(Company.objects.filter(source=Company.UKRAINE_REGISTER).values_list('id', flat=True))
        self.uptodated_companies = []
        super().__init__()

    def save_or_get_bylaw(self, bylaw_from_record):
        if bylaw_from_record not in self.all_bylaw_dict:
            new_bylaw = Bylaw.objects.create(name=bylaw_from_record)
            self.all_bylaw_dict[bylaw_from_record] = new_bylaw
            return new_bylaw
        return self.all_bylaw_dict[bylaw_from_record]

    def save_or_get_predecessor(self, item):
        if item.xpath('NAME')[0].text not in self.all_predecessors_dict or \
                (hasattr(self.all_predecessors_dict, item.xpath('NAME')[0].text) and item.xpath('CODE')[0].text != \
                 self.all_predecessors_dict[item.xpath('NAME')[0].text].code):
            new_predecessor = Predecessor.objects.create(
                name=item.xpath('NAME')[0].text.lower(),
                edrpou=item.xpath('CODE')[0].text
            )
            self.all_predecessors_dict[item.xpath('NAME')[0].text] = new_predecessor
            return new_predecessor
        return self.all_predecessors_dict[item.xpath('NAME')[0].text]

    def extract_detail_founder_data(self, founder_info):
        info_to_list = founder_info.split(',')
        # deleting spaces between strings if exist
        info_to_list = [string.strip() for string in info_to_list]
        # getting first element that is a name
        name = info_to_list[0]
        # checking if second element is a EDRPOU code
        edrpou = info_to_list[1] if self.find_edrpou(info_to_list[1]) else None
        # checking if other element is an EDRPOU code in case if the name has commas inside
        if not edrpou:
            for string in info_to_list:
                if self.find_edrpou(string):
                    edrpou = string
                    # getting the name with commas inside
                    info_to_new_list = founder_info.split(string)
                    name = info_to_new_list[0]
                    # logger.warning(f'Нестандартний запис: {founder_info}')
                    break
        equity = None
        element_with_equity = None
        # usually equity is at the end of the record
        for string in info_to_list:
            if string.startswith('розмір внеску до статутного фонду') and string.endswith('грн.'):
                element_with_equity = string
                equity = float(re.findall('\d+\.\d+', string)[0])
                break
        # deleting all info except the address
        address = founder_info.replace(name, '')
        if edrpou:
            address = address.replace(edrpou, '')
        if element_with_equity:
            address = address.replace(element_with_equity, '')
        if address and len(address) < 15:
            address = None
        # if address and len(address) > 200:
            # logger.warning(f'Завелика адреса: {address} із запису: {founder_info}')
        return name, edrpou, address, equity

    def extract_founder_data(self, founder_info):
        # split by first comma that usually separates name and equity that also has comma
        info_to_list = founder_info.split(',', 1)
        info_to_list = [string.strip() for string in info_to_list]
        name = info_to_list[0]
        is_beneficiary = False
        if name.startswith('КІНЦЕВИЙ БЕНЕФІЦІАРНИЙ ВЛАСНИК'):
            is_beneficiary = True
        second_part = info_to_list[1]
        equity = None
        address = None
        if second_part.startswith('розмір частки'):
            digital_value = re.findall('\d+\,\d+', second_part)[0]
            equity = float(digital_value.replace(',', '.'))
        else:
            address = second_part
        return name, is_beneficiary, address, equity

    def extract_beneficiary_data(self, beneficiary_info):
        # split by semicolons that usually separates name, country and address
        info_to_list = beneficiary_info.split(';', 3)
        info_to_list = [string.strip() for string in info_to_list]
        if info_to_list[0].lower() == 'україна' and len(info_to_list) == 4:
            country, address, edrpou, name = [item for item in info_to_list]
        elif len(info_to_list) == 3:
            name, country, address = [item for item in info_to_list]
            edrpou = None
        else:
            name, country, address, edrpou = beneficiary_info, None, None, None
        return name, country, address, edrpou

    def add_founders(self, founders_from_record, beneficiaries_from_record, code):
        self.founder_to_dict[code] = []
        for item in founders_from_record:
            info = item.text
            # checking if field contains data
            if not info or info.endswith('ВІДСУТНІЙ'):
                continue
            # checking if there is additional data except name
            if ',' in item.text:
                name, edrpou, address, equity = self.extract_detail_founder_data(item.text)
                name = name.lower()
            else:
                name = item.text.lower()
                edrpou, equity, address = None, None, None
            country = None
            is_beneficiary = False
            info_beneficiary = None
            for beneficiary in beneficiaries_from_record:
                name_beneficiary, country_beneficiary, address_beneficiary, edrpou_beneficiary =\
                    self.extract_beneficiary_data(beneficiary.text)
                name_beneficiary = name_beneficiary.lower()
                if name_beneficiary == name:
                    info_beneficiary = beneficiary.text
                    country = country_beneficiary.lower()
                    address = address_beneficiary
                    edrpou = edrpou_beneficiary or edrpou
                    is_beneficiary = True
                    beneficiaries_from_record.remove(beneficiary)
                    break
            founder = Founder(
                info=info,
                info_beneficiary=info_beneficiary,
                name=name,
                edrpou=edrpou,
                address=address,
                equity=equity,
                country=country,
                is_beneficiary=is_beneficiary,
                is_founder=True
            )
            self.founder_to_dict[code].append(founder)
        for beneficiary in beneficiaries_from_record:
            name_beneficiary, country_beneficiary, address_beneficiary, edrpou_beneficiary = \
                self.extract_beneficiary_data(beneficiary.text)
            name = name_beneficiary.lower()
            info_beneficiary = beneficiary.text
            country = country_beneficiary.lower() if country_beneficiary else None
            address = address_beneficiary
            founder = Founder(
                info_beneficiary=info_beneficiary,
                name=name,
                address=address,
                country=country,
                edrpou=edrpou_beneficiary,
                is_beneficiary=True,
                is_founder=False
            )
            self.founder_to_dict[code].append(founder)

    def update_founders(self, founders_from_record, beneficiaries_from_record, company):
        already_stored_founders = list(Founder.include_deleted_objects.filter(company_id=company.id))
        for item in founders_from_record:
            info = item.text
            # checking if field contains data
            if not info or info.endswith('ВІДСУТНІЙ'):
                continue
            # checking if there is additional data except name
            if ',' in item.text:
                name, edrpou, address, equity = self.extract_detail_founder_data(item.text)
                name = name.lower()
            else:
                name = item.text.lower()
                edrpou, equity, address = None, None, None
            country = None
            is_beneficiary = False
            info_beneficiary = None
            for beneficiary in beneficiaries_from_record:
                name_beneficiary, country_beneficiary, address_beneficiary, edrpou_beneficiary = \
                    self.extract_beneficiary_data(beneficiary.text)
                name_beneficiary = name_beneficiary.lower()
                if name_beneficiary == name:
                    info_beneficiary = beneficiary.text
                    country = country_beneficiary.lower()
                    address = address_beneficiary
                    edrpou = edrpou_beneficiary or edrpou
                    is_beneficiary = True
                    beneficiaries_from_record.remove(beneficiary)
                    break
            already_stored = False
            if len(already_stored_founders):
                for stored_founder in already_stored_founders:
                    if stored_founder.name == name:
                        already_stored = True
                        if stored_founder.info != info or stored_founder.info_beneficiary != info_beneficiary:
                            update_fields = []
                            stored_founder.info = info
                            stored_founder.info_beneficiary = info_beneficiary
                            update_fields.extend(['info', 'info_beneficiary'])
                            if stored_founder.is_beneficiary != is_beneficiary:
                                stored_founder.is_beneficiary = is_beneficiary
                                update_fields.append('is_beneficiary')
                            if address and stored_founder.address != address:
                                stored_founder.address = address
                                update_fields.append('address')
                            if equity and stored_founder.equity != equity:
                                stored_founder.equity = equity
                                update_fields.append('equity')
                            if edrpou and stored_founder.edrpou != edrpou:
                                stored_founder.edrpou = edrpou
                                update_fields.append('edrpou')
                            if country and stored_founder.country != country:
                                stored_founder.country = country
                                update_fields.append('country')
                            if stored_founder.deleted_at:
                                stored_founder.deleted_at = None
                                update_fields.append('deleted_at')
                            if update_fields:
                                update_fields.append('updated_at')
                                stored_founder.save(update_fields=update_fields)
                        already_stored_founders.remove(stored_founder)
                        break
            if not already_stored:
                founder = Founder(
                    company_id=company.id,
                    info=info,
                    info_beneficiary=info_beneficiary,
                    name=name,
                    edrpou=edrpou,
                    address=address,
                    equity=equity,
                    country=country,
                    is_beneficiary=is_beneficiary,
                    is_founder=True
                )
                self.bulk_manager.add(founder)
        for beneficiary in beneficiaries_from_record:
            name_beneficiary, country_beneficiary, address_beneficiary, edrpou_beneficiary = \
                self.extract_beneficiary_data(beneficiary.text)
            name = name_beneficiary.lower()
            info_beneficiary = beneficiary.text
            if country_beneficiary:
                country_beneficiary = country_beneficiary.lower()
            already_stored = False
            if len(already_stored_founders):
                for stored_founder in already_stored_founders:
                    if stored_founder.name == name:
                        already_stored = True
                        if stored_founder.info_beneficiary != info_beneficiary:
                            stored_founder.info_beneficiary = info_beneficiary
                            stored_founder.address = address_beneficiary
                            stored_founder.country = country_beneficiary
                            stored_founder.edrpou = edrpou_beneficiary
                            stored_founder.is_beneficiary = True
                            stored_founder.is_founder = False
                            update_fields = ['info_beneficiary', 'address', 'country', 'edrpou', 'is_beneficiary',
                                             'is_founder']
                            if stored_founder.deleted_at:
                                stored_founder.deleted_at = None
                                update_fields.append('deleted_at')
                            update_fields.append('updated_at')
                            stored_founder.save(update_fields=update_fields)
                        already_stored_founders.remove(stored_founder)
                        break
            if not already_stored:
                founder = Founder(
                    company_id=company.id,
                    info_beneficiary=info_beneficiary,
                    name=name,
                    address=address_beneficiary,
                    country=country_beneficiary,
                    edrpou=edrpou_beneficiary,
                    is_beneficiary=True,
                    is_founder=False
                )

                if country_beneficiary and len(country_beneficiary) > 100:
                    print('country', country_beneficiary, 'name', name, 'address', address)
                self.bulk_manager.add(founder)
        if len(already_stored_founders):
            for outdated_founder in already_stored_founders:
                outdated_founder.soft_delete()

    def add_company_detail(self, founding_document_number, executive_power, superior_management,
                           managing_paper, terminated_info, termination_cancel_info, vp_dates,
                           code):
        company_detail = CompanyDetail()
        company_detail.founding_document_number = founding_document_number
        company_detail.executive_power = executive_power
        company_detail.superior_management = superior_management
        company_detail.managing_paper = managing_paper
        company_detail.terminated_info = terminated_info
        company_detail.termination_cancel_info = termination_cancel_info
        company_detail.vp_dates = vp_dates
        self.company_detail_to_dict[code] = company_detail

    def update_company_detail(self, founding_document_number, executive_power, superior_management,
                              managing_paper, terminated_info, termination_cancel_info, vp_dates,
                              company):
        company_detail = CompanyDetail.include_deleted_objects.filter(company_id=company.id).first()
        if company_detail:
            update_fields = []
            if company_detail.founding_document_number != founding_document_number:
                company_detail.founding_document_number = founding_document_number
                update_fields.append('founding_document_number')
            if company_detail.executive_power != executive_power:
                company_detail.executive_power = executive_power
                update_fields.append('executive_power')
            if company_detail.superior_management != superior_management:
                company_detail.superior_management = superior_management
                update_fields.append('superior_management')
            if company_detail.managing_paper != managing_paper:
                company_detail.managing_paper = managing_paper
                update_fields.append('managing_paper')
            if company_detail.terminated_info != terminated_info:
                company_detail.terminated_info = terminated_info
                update_fields.append('terminated_info')
            if company_detail.termination_cancel_info != termination_cancel_info:
                company_detail.termination_cancel_info = termination_cancel_info
                update_fields.append('termination_cancel_info')
            if company_detail.vp_dates != vp_dates:
                company_detail.vp_dates = vp_dates
                update_fields.append('vp_dates')
            if company_detail.deleted_at:
                company_detail.deleted_at = None
                update_fields.append('deleted_at')
            if len(update_fields):
                update_fields.append('updated_at')
                company_detail.save(update_fields=update_fields)
        else:
            company_detail = CompanyDetail()
            company_detail.founding_document_number = founding_document_number
            company_detail.executive_power = executive_power
            company_detail.superior_management = superior_management
            company_detail.managing_paper = managing_paper
            company_detail.terminated_info = terminated_info
            company_detail.termination_cancel_info = termination_cancel_info
            company_detail.vp_dates = vp_dates
            company_detail.company = company
            self.bulk_manager.add(company_detail)

    def add_assignees(self, assignees_from_record, code):
        assignees = []
        for item in assignees_from_record:
            assignee = Assignee()
            if item.xpath('NAME')[0].text:
                assignee.name = item.xpath('NAME')[0].text.lower()
            else:
                assignee.name = ''
            assignee.edrpou = item.xpath('CODE')[0].text
            if not assignee.edrpou:
                assignee.edrpou = ''
            if assignee.name or assignee.edrpou:
                assignees.append(assignee)
        self.assignee_to_dict[code] = assignees

    def update_assignees(self, assignees_from_record, company):
        already_stored_assignees = list(Assignee.include_deleted_objects.filter(company_id=company.id))
        for item in assignees_from_record:
            name = item.xpath('NAME')[0].text
            if name:
                name = name.lower()
            else:
                name = ''
            edrpou = item.xpath('CODE')[0].text
            if not edrpou:
                edrpou = ''
            if not name and not edrpou:
                continue
            already_stored = False
            if len(already_stored_assignees):
                for stored_assignee in already_stored_assignees:
                    if stored_assignee.name == name and stored_assignee.edrpou == edrpou:
                        already_stored = True
                        if stored_assignee.deleted_at:
                            stored_assignee.deleted_at = None
                            stored_assignee.save(update_fields=['deleted_at', 'updated_at'])
                        already_stored_assignees.remove(stored_assignee)
                        break
            if not already_stored:
                assignee = Assignee()
                assignee.name = name
                assignee.edrpou = edrpou
                assignee.company = company
                self.bulk_manager.add(assignee)
        if len(already_stored_assignees):
            for outdated_assignees in already_stored_assignees:
                outdated_assignees.soft_delete()

    def add_bancruptcy_readjustment(self, record, code):
        bancruptcy_readjustment = BancruptcyReadjustment()
        bancruptcy_readjustment.op_date = format_date_to_yymmdd(
            record.xpath('BANKRUPTCY_READJUSTMENT_INFO/OP_DATE')[0].text) or None
        bancruptcy_readjustment.reason = record.xpath(
            'BANKRUPTCY_READJUSTMENT_INFO/REASON')[0].text.lower()
        bancruptcy_readjustment.sbj_state = record.xpath(
            'BANKRUPTCY_READJUSTMENT_INFO/SBJ_STATE')[0].text.lower()
        if record.xpath('BANKRUPTCY_READJUSTMENT_INFO/BANKRUPTCY_READJUSTMENT_HEAD_NAME'):
            head_name = record.xpath('BANKRUPTCY_READJUSTMENT_INFO/BANKRUPTCY_READJUSTMENT_HEAD_NAME')[0].text
            if head_name:
                bancruptcy_readjustment.head_name = head_name.lower()
        self.bancruptcy_readjustment_to_dict[code] = bancruptcy_readjustment

    def update_bancruptcy_readjustment(self, record, company):
        already_stored_bancruptcy_readjustment = \
            BancruptcyReadjustment.include_deleted_objects.filter(company_id=company.id).first()
        if record.xpath('BANKRUPTCY_READJUSTMENT_INFO/OP_DATE'):
            op_date = format_date_to_yymmdd(record.xpath('BANKRUPTCY_READJUSTMENT_INFO/OP_DATE')[0].text) or None
            reason = record.xpath('BANKRUPTCY_READJUSTMENT_INFO/REASON')[0].text.lower()
            sbj_state = record.xpath('BANKRUPTCY_READJUSTMENT_INFO/SBJ_STATE')[0].text.lower()
            if record.xpath('BANKRUPTCY_READJUSTMENT_INFO/BANKRUPTCY_READJUSTMENT_HEAD_NAME'):
                head_name = record.xpath('BANKRUPTCY_READJUSTMENT_INFO/BANKRUPTCY_READJUSTMENT_HEAD_NAME')[0].text
                if head_name:
                    head_name = head_name.lower()
            else:
                head_name = None
            if not already_stored_bancruptcy_readjustment:
                bancruptcy_readjustment = BancruptcyReadjustment()
                bancruptcy_readjustment.company = company
                bancruptcy_readjustment.op_date = op_date
                bancruptcy_readjustment.reason = reason
                bancruptcy_readjustment.sbj_state = sbj_state
                bancruptcy_readjustment.head_name = head_name
                self.bulk_manager.add(bancruptcy_readjustment)
                return
            else:
                update_fields = []
                if already_stored_bancruptcy_readjustment.op_date != op_date:
                    already_stored_bancruptcy_readjustment.op_date = op_date
                    update_fields.append('op_date')
                if already_stored_bancruptcy_readjustment.reason != reason:
                    already_stored_bancruptcy_readjustment.reason = reason
                    update_fields.append('reason')
                if already_stored_bancruptcy_readjustment.sbj_state != sbj_state:
                    already_stored_bancruptcy_readjustment.sbj_state = sbj_state
                    update_fields.append('sbj_state')
                if already_stored_bancruptcy_readjustment.head_name != head_name:
                    already_stored_bancruptcy_readjustment.head_name = head_name
                    update_fields.append('head_name')
                if already_stored_bancruptcy_readjustment.deleted_at:
                    already_stored_bancruptcy_readjustment.deleted_at = None
                    update_fields.append('deleted_at')
                if len(update_fields):
                    update_fields.append('updated_at')
                    already_stored_bancruptcy_readjustment.save(update_fields=update_fields)
        elif already_stored_bancruptcy_readjustment:
            already_stored_bancruptcy_readjustment.soft_delete()

    def add_company_to_kved(self, kveds_from_record, code):
        company_to_kveds = []
        for item in kveds_from_record:
            if not item.xpath('NAME'):
                continue
            kved_code = item.xpath('CODE')[0].text
            kved_name = item.xpath('NAME')[0].text
            if not kved_name:
                continue
            if not kved_code:
                kved_code = ''
            company_to_kved = CompanyToKved()
            company_to_kved.kved = self.get_kved_from_DB(kved_code, kved_name)
            if item.xpath('PRIMARY'):
                company_to_kved.primary_kved = item.xpath('PRIMARY')[0].text == "так"
            company_to_kveds.append(company_to_kved)
        self.company_to_kved_to_dict[code] = company_to_kveds

    def update_company_to_kved(self, kveds_from_record, company):
        already_stored_company_to_kved = list(CompanyToKved.include_deleted_objects.filter(company_id=company.id))
        for item in kveds_from_record:
            if not item.xpath('NAME'):
                continue
            kved_code = item.xpath('CODE')[0].text
            kved_name = item.xpath('NAME')[0].text
            if not kved_name:
                continue
            if not kved_code:
                kved_code = ''
            already_stored = False
            kved_from_db = self.get_kved_from_DB(kved_code, kved_name)
            if len(already_stored_company_to_kved):
                for stored_company_to_kved in already_stored_company_to_kved:
                    if stored_company_to_kved.kved_id == kved_from_db.id:
                        already_stored = True
                        update_fields = []
                        if item.xpath('PRIMARY'):
                            if stored_company_to_kved.primary_kved != (item.xpath('PRIMARY')[0].text == "так"):
                                stored_company_to_kved.primary_kved = item.xpath('PRIMARY')[0].text == "так"
                                update_fields.append('primary_kved')
                        if stored_company_to_kved.deleted_at:
                            stored_company_to_kved.deleted_at = None
                            update_fields.append('deleted_at')
                        if len(update_fields):
                            update_fields.append('updated_at')
                            stored_company_to_kved.save(update_fields=update_fields)
                        already_stored_company_to_kved.remove(stored_company_to_kved)
                        break
            if not already_stored:
                company_to_kved = CompanyToKved()
                company_to_kved.company = company
                company_to_kved.kved = kved_from_db
                if item.xpath('PRIMARY'):
                    company_to_kved.primary_kved = item.xpath('PRIMARY')[0].text == "так"
                self.bulk_manager.add(company_to_kved)
        if len(already_stored_company_to_kved):
            for outdated_company_to_kved in already_stored_company_to_kved:
                outdated_company_to_kved.soft_delete()

    def add_exchange_data(self, exchange_data_from_record, code):
        exchange_datas = []
        for item in exchange_data_from_record:
            if item.xpath('AUTHORITY_NAME') and item.xpath('AUTHORITY_NAME')[0].text:
                exchange_data = ExchangeDataCompany()
                exchange_data.authority = self.save_or_get_authority(item.xpath(
                    'AUTHORITY_NAME')[0].text)
                if item.xpath('TAX_PAYER_TYPE'):
                    taxpayer_type = item.xpath('TAX_PAYER_TYPE')[0].text
                    exchange_data.taxpayer_type = self.save_or_get_taxpayer_type(taxpayer_type)
                if item.xpath('START_DATE'):
                    exchange_data.start_date = format_date_to_yymmdd(
                        item.xpath('START_DATE')[0].text) or None
                if item.xpath('START_NUM'):
                    exchange_data.start_number = item.xpath('START_NUM')[0].text
                if item.xpath('END_DATE'):
                    exchange_data.end_date = format_date_to_yymmdd(
                        item.xpath('END_DATE')[0].text) or None
                if item.xpath('END_NUM'):
                    exchange_data.end_number = item.xpath('END_NUM')[0].text
                exchange_datas.append(exchange_data)
            self.exchange_data_to_dict[code] = exchange_datas

    def update_exchange_data(self, exchange_data_from_record, company):
        already_stored_exchange_data = list(ExchangeDataCompany.include_deleted_objects.filter(company_id=company.id))
        for item in exchange_data_from_record:
            if not item.xpath('NAME'):
                continue
            authority = self.save_or_get_authority(item.xpath('AUTHORITY_NAME')[0].text)
            taxpayer_type = item.xpath('TAX_PAYER_TYPE')[0].text
            start_date, end_date = None, None
            if taxpayer_type:
                taxpayer_type = self.save_or_get_taxpayer_type(taxpayer_type)
            if item.xpath('START_DATE')[0].text:
                start_date = format_date_to_yymmdd(item.xpath('START_DATE')[0].text) or None
            start_number = item.xpath('START_NUM')[0].text
            if item.xpath('END_DATE')[0].text:
                end_date = format_date_to_yymmdd(item.xpath('END_DATE')[0].text) or None
            end_number = item.xpath('END_NUM')[0].text
            already_stored = False
            if len(already_stored_exchange_data):
                for stored_exchange_data in already_stored_exchange_data:
                    if stored_exchange_data.authority_id == authority.id and \
                            stored_exchange_data.start_date == start_date:
                        already_stored = True
                        update_fields = []
                        if stored_exchange_data.start_number != start_number:
                            stored_exchange_data.start_number = start_number
                            update_fields.append('start_number')
                        if stored_exchange_data.taxpayer_type_id != taxpayer_type.id:
                            stored_exchange_data.taxpayer_type = taxpayer_type
                            update_fields.append('taxpayer_type')
                        if stored_exchange_data.end_date != end_date:
                            stored_exchange_data.end_date = end_date
                            update_fields.append('end_date')
                        if stored_exchange_data.end_number != end_number:
                            stored_exchange_data.end_number = end_number
                            update_fields.append('end_number')
                        if stored_exchange_data.deleted_at:
                            stored_exchange_data.deleted_at = None
                            update_fields.append('deleted_at')
                        if len(update_fields):
                            update_fields.append('updated_at')
                            stored_exchange_data.save(update_fields=update_fields)
                        already_stored_exchange_data.remove(stored_exchange_data)
            if not already_stored:
                exchange_data = ExchangeDataCompany()
                exchange_data.authority = authority
                exchange_data.taxpayer_type = taxpayer_type
                exchange_data.start_date = start_date
                exchange_data.start_number = start_number
                exchange_data.end_date = end_date
                exchange_data.end_number = end_number
                exchange_data.company = company
                self.bulk_manager.add(exchange_data)
        if len(already_stored_exchange_data):
            for outdated_exchange_data in already_stored_exchange_data:
                outdated_exchange_data.soft_delete()

    def add_company_to_predecessors(self, predecessors_from_record, code):
        company_to_predecessors = []
        for item in predecessors_from_record:
            if item.xpath('NAME')[0].text:
                company_to_predecessor = CompanyToPredecessor()
                company_to_predecessor.predecessor = self.save_or_get_predecessor(item)
                company_to_predecessors.append(company_to_predecessor)
        self.company_to_predecessor_to_dict[code] = company_to_predecessors

    def update_company_to_predecessors(self, predecessors_from_record, company):
        already_stored_company_to_predecessors = \
            list(CompanyToPredecessor.include_deleted_objects.filter(company_id=company.id))
        for item in predecessors_from_record:
            if item.xpath('NAME')[0].text:
                already_stored = False
                predecessor = self.save_or_get_predecessor(item)
                if len(already_stored_company_to_predecessors):
                    for stored_predecessor in already_stored_company_to_predecessors:
                        if stored_predecessor.predecessor_id == predecessor.id:
                            already_stored = True
                            if stored_predecessor.deleted_at:
                                stored_predecessor.deleted_at = None
                                stored_predecessor.save(update_fields=['deleted_at', 'updated_at'])
                            already_stored_company_to_predecessors.remove(stored_predecessor)
                            break
                if not already_stored:
                    company_to_predecessor = CompanyToPredecessor()
                    company_to_predecessor.predecessor = predecessor
                    company_to_predecessor.company = company
                    self.bulk_manager.add(company_to_predecessor)
        if len(already_stored_company_to_predecessors):
            for outdated_company_to_predecessors in already_stored_company_to_predecessors:
                outdated_company_to_predecessors.soft_delete()

    def add_signers(self, signers_from_record, code):
        signers = []
        for item in signers_from_record:
            signer = Signer()
            signer.name = item.text[:389].lower()
            signers.append(signer)
        self.signer_to_dict[code] = signers

    def update_signers(self, signers_from_record, company):
        already_stored_signers = list(Signer.include_deleted_objects.filter(company_id=company.id))
        for item in signers_from_record:
            already_stored = False
            if len(already_stored_signers):
                for stored_signer in already_stored_signers:
                    if stored_signer.name == item.text[:389].lower():
                        already_stored = True
                        if stored_signer.deleted_at:
                            stored_signer.deleted_at = None
                            stored_signer.save(update_fields=['deleted_at', 'updated_at'])
                        already_stored_signers.remove(stored_signer)
                        break
            if not already_stored:
                signer = Signer()
                signer.name = item.text[:389].lower()
                signer.company = company
                self.bulk_manager.add(signer)
        if len(already_stored_signers):
            for outdated_signers in already_stored_signers:
                outdated_signers.soft_delete()

    def add_termination_started(self, record, code):
        termination_started = TerminationStarted()
        if record.xpath('TERMINATION_STARTED_INFO/OP_DATE')[0].text:
            termination_started.op_date = format_date_to_yymmdd(
                record.xpath('TERMINATION_STARTED_INFO/OP_DATE')[0].text) or None
        termination_started.reason = record.xpath('TERMINATION_STARTED_INFO'
                                                  '/REASON')[0].text.lower()
        termination_started.sbj_state = record.xpath(
            'TERMINATION_STARTED_INFO/SBJ_STATE')[0].text.lower()
        if record.xpath('TERMINATION_STARTED_INFO/SIGNER_NAME'):
            signer_name = record.xpath('TERMINATION_STARTED_INFO/SIGNER_NAME')[0].text
            if signer_name:
                termination_started.signer_name = signer_name.lower()
        if record.xpath('TERMINATION_STARTED_INFO/CREDITOR_REQ_END_DATE'):
            termination_started.creditor_reg_end_date = format_date_to_yymmdd(
                record.xpath('TERMINATION_STARTED_INFO/CREDITOR_REQ_END_DATE')[0].text) or '1990-01-01'
        self.termination_started_to_dict[code] = termination_started

    def update_termination_started(self, record, company):
        already_stored_termination_started = \
            TerminationStarted.include_deleted_objects.filter(company_id=company.id).first()
        if record.xpath('TERMINATION_STARTED_INFO/OP_DATE'):
            op_date = format_date_to_yymmdd(record.xpath('TERMINATION_STARTED_INFO/OP_DATE')[0].text) or None
            reason = record.xpath('TERMINATION_STARTED_INFO/REASON')[0].text.lower()
            sbj_state = record.xpath('TERMINATION_STARTED_INFO/SBJ_STATE')[0].text.lower()
            if record.xpath('TERMINATION_STARTED_INFO/SIGNER_NAME'):
                signer_name = record.xpath('TERMINATION_STARTED_INFO/SIGNER_NAME')[0].text
                if signer_name:
                    signer_name = signer_name.lower()
            else:
                signer_name = None
            if record.xpath('TERMINATION_STARTED_INFO/CREDITOR_REQ_END_DATE'):
                creditor_reg_end_date = format_date_to_yymmdd(
                    record.xpath('TERMINATION_STARTED_INFO/CREDITOR_REQ_END_DATE')[0].text) or '1990-01-01'
            else:
                creditor_reg_end_date = '1990-01-01'
            if not already_stored_termination_started:
                termination_started = TerminationStarted()
                termination_started.company = company
                termination_started.op_date = op_date
                termination_started.reason = reason
                termination_started.sbj_state = sbj_state
                termination_started.signer_name = signer_name
                termination_started.creditor_reg_end_date = creditor_reg_end_date
                self.bulk_manager.add(termination_started)
                return
            else:
                update_fields = []
                if already_stored_termination_started.op_date != op_date:
                    already_stored_termination_started.op_date = op_date
                    update_fields.append('op_date')
                if already_stored_termination_started.reason != reason:
                    already_stored_termination_started.reason = reason
                    update_fields.append('reason')
                if already_stored_termination_started.sbj_state != sbj_state:
                    already_stored_termination_started.sbj_state = sbj_state
                    update_fields.append('sbj_state')
                if already_stored_termination_started.signer_name != signer_name:
                    already_stored_termination_started.signer_name = signer_name
                    update_fields.append('signer_name')
                if already_stored_termination_started.creditor_reg_end_date != creditor_reg_end_date:
                    already_stored_termination_started.creditor_reg_end_date = creditor_reg_end_date
                    update_fields.append('creditor_reg_end_date')
                if already_stored_termination_started.deleted_at:
                    already_stored_termination_started.deleted_at = None
                    update_fields.append('deleted_at')
                if len(update_fields):
                    update_fields.append('updated_at')
                    already_stored_termination_started.save(update_fields=update_fields)
        elif already_stored_termination_started:
            already_stored_termination_started.soft_delete()

    def save_to_db(self, records):
        for record in records:
            edrpou = record.xpath('EDRPOU')[0].text
            if not edrpou:
                continue
            if record.xpath('NAME')[0].text:
                name = record.xpath('NAME')[0].text.lower()
            else:
                continue
            code = name + edrpou
            address = record.xpath('ADDRESS')[0].text
            founding_document_number = record.xpath('FOUNDING_DOCUMENT_NUM')[0].text
            contact_info = record.xpath('CONTACTS')[0].text
            vp_dates = record.xpath('VP_DATES')[0].text
            short_name = record.xpath('SHORT_NAME')[0].text
            if short_name:
                short_name = short_name.lower()
            executive_power = record.xpath('EXECUTIVE_POWER')[0].text
            if executive_power:
                executive_power = executive_power.lower()
            superior_management = record.xpath('SUPERIOR_MANAGEMENT')[0].text
            if superior_management:
                superior_management = superior_management.lower()
            managing_paper = record.xpath('MANAGING_PAPER')[0].text
            if managing_paper:
                managing_paper = managing_paper.lower()
            terminated_info = record.xpath('TERMINATED_INFO')[0].text
            if terminated_info:
                terminated_info = terminated_info.lower()
            termination_cancel_info = record.xpath('TERMINATION_CANCEL_INFO')[0].text
            if termination_cancel_info:
                termination_cancel_info = termination_cancel_info.lower()
            authorized_capital = record.xpath('AUTHORIZED_CAPITAL')[0].text
            if authorized_capital:
                authorized_capital = authorized_capital.replace(',', '.')
                authorized_capital = float(authorized_capital)
            registration_date = None
            registration_info = None
            registration = record.xpath('REGISTRATION')[0].text
            if registration:
                registration_date = format_date_to_yymmdd(get_first_word(registration))
                registration_info = cut_first_word(registration)
            company_type = record.xpath('OPF')[0].text
            if company_type:
                company_type = self.save_or_get_company_type(company_type, 'uk')
            status = self.save_or_get_status(record.xpath('STAN')[0].text)
            bylaw = self.save_or_get_bylaw(record.xpath('STATUTE')[0].text)
            authority = record.xpath('CURRENT_AUTHORITY')[0].text
            if authority:
                authority = self.save_or_get_authority(authority)
            else:
                authority = None
            self.time_it('getting data from record')

            company = Company.include_deleted_objects.filter(code=code, source=Company.UKRAINE_REGISTER).first()
            self.time_it('trying get companies\t')

            if not company:
                company = Company(
                    name=name,
                    short_name=short_name,
                    company_type=company_type,
                    edrpou=edrpou,
                    country=self.company_country,
                    address=address,
                    authorized_capital=authorized_capital,
                    status=status,
                    bylaw=bylaw,
                    registration_date=registration_date,
                    registration_info=registration_info,
                    contact_info=contact_info,
                    authority=authority,
                    source=self.source,
                    code=code
                )
                self.bulk_manager.add(company)
                self.add_company_detail(founding_document_number, executive_power, superior_management, managing_paper,
                                        terminated_info, termination_cancel_info, vp_dates, code)
                if len(record.xpath('ACTIVITY_KINDS')[0]):
                    self.add_company_to_kved(record.xpath('ACTIVITY_KINDS')[0], code)
                if len(record.xpath('SIGNERS')[0]):
                    self.add_signers(record.xpath('SIGNERS')[0], code)
                if record.xpath('TERMINATION_STARTED_INFO/OP_DATE'):
                    self.add_termination_started(record, code)
                if record.xpath('BANKRUPTCY_READJUSTMENT_INFO/OP_DATE'):
                    self.add_bancruptcy_readjustment(record, code)
                if len(record.xpath('PREDECESSORS')[0]):
                    self.add_company_to_predecessors(record.xpath('PREDECESSORS')[0], code)
                if len(record.xpath('ASSIGNEES')[0]):
                    self.add_assignees(record.xpath('ASSIGNEES')[0], code)
                if len(record.xpath('EXCHANGE_DATA')[0]):
                    self.add_exchange_data(record.xpath('EXCHANGE_DATA')[0], code)
                self.add_founders(record.xpath('FOUNDERS')[0] if len(record.xpath('FOUNDERS')[0]) else [],
                                  record.xpath('BENEFICIARIES')[0] if len(record.xpath('BENEFICIARIES')[0]) else [],
                                  code)
                self.time_it('save companies\t')
            else:
                self.uptodated_companies.append(company.id)
                update_fields = []
                if company.name != name:
                    company.name = name
                    update_fields.append('name')
                if company.short_name != short_name:
                    company.short_name = short_name
                    update_fields.append('short_name')
                if company_type:
                    if company.company_type_id != company_type.id:
                        company.company_type = company_type
                        update_fields.append('company_type')
                elif company.company_type_id:
                    company.company_type = None
                    update_fields.append('company_type')
                if company.authorized_capital != authorized_capital:
                    company.authorized_capital = authorized_capital
                    update_fields.append('authorized_capital')
                if company.address != address:
                    company.address = address
                    update_fields.append('address')
                if company.status_id != status.id:
                    company.status = status
                    update_fields.append('status')
                if company.bylaw_id != bylaw.id:
                    company.bylaw = bylaw
                    update_fields.append('bylaw')
                if to_lower_string_if_exists(company.registration_date) != registration_date:
                    company.registration_date = registration_date
                    update_fields.append('registration_date')
                if company.registration_info != registration_info:
                    company.registration_info = registration_info
                    update_fields.append('registration_info')
                if company.contact_info != contact_info:
                    company.contact_info = contact_info
                    update_fields.append('contact_info')
                if authority:
                    if company.authority_id != authority.id:
                        company.authority = authority
                        update_fields.append('authority')
                else:
                    if company.authority_id:
                        company.authority = None
                        update_fields.append('authority')
                if company.country_id != self.company_country.id:
                    company.country = self.company_country
                    update_fields.append('country')
                if company.deleted_at:
                    company.deleted_at = None
                    update_fields.append('deleted_at')
                if update_fields:
                    update_fields.append('updated_at')
                    company.save(update_fields=update_fields)
                self.time_it('update companies\t')
                self.update_company_detail(founding_document_number, executive_power, superior_management,
                                           managing_paper, terminated_info, termination_cancel_info, vp_dates, company)
                self.time_it('update company details\t')
                self.update_founders(record.xpath('FOUNDERS')[0] if len(record.xpath('FOUNDERS')[0]) else [],
                                  record.xpath('BENEFICIARIES')[0] if len(record.xpath('BENEFICIARIES')[0]) else [],
                                  company)
                self.time_it('update founders\t\t')
                self.update_company_to_kved(record.xpath('ACTIVITY_KINDS')[0], company)
                self.time_it('update kveds\t\t')
                self.update_signers(record.xpath('SIGNERS')[0], company)
                self.time_it('update signers\t\t')
                self.update_termination_started(record, company)
                self.time_it('update termination\t')
                self.update_bancruptcy_readjustment(record, company)
                self.time_it('update bancruptcy\t')
                self.update_company_to_predecessors(record.xpath('PREDECESSORS')[0], company)
                self.time_it('update predecessors\t')
                self.update_assignees(record.xpath('ASSIGNEES')[0], company)
                self.time_it('update assignes\t\t')
                self.update_exchange_data(record.xpath('EXCHANGE_DATA')[0], company)
                self.time_it('update exchange data\t')

        if len(self.bulk_manager.queues['business_register.Company']):
            self.bulk_manager.commit(Company)
        for company in self.bulk_manager.queues['business_register.Company']:
            code = company.code
            if code in self.founder_to_dict:
                for founder in self.founder_to_dict[code]:
                    founder.company = company
                    self.bulk_manager.add(founder)
            if code in self.signer_to_dict:
                for signer in self.signer_to_dict[code]:
                    signer.company = company
                    self.bulk_manager.add(signer)
            if code in self.assignee_to_dict:
                for assignee in self.assignee_to_dict[code]:
                    assignee.company = company
                    self.bulk_manager.add(assignee)
            if code in self.company_to_predecessor_to_dict:
                for company_to_predecessor in self.company_to_predecessor_to_dict[code]:
                    company_to_predecessor.company = company
                    self.bulk_manager.add(company_to_predecessor)
            if code in self.exchange_data_to_dict:
                for exchange_data in self.exchange_data_to_dict[code]:
                    exchange_data.company = company
                    self.bulk_manager.add(exchange_data)
            if code in self.company_to_kved_to_dict:
                for company_to_kved in self.company_to_kved_to_dict[code]:
                    company_to_kved.company = company
                    self.bulk_manager.add(company_to_kved)
            if code in self.company_detail_to_dict:
                self.company_detail_to_dict[code].company = company
                self.bulk_manager.add(self.company_detail_to_dict[code])
            if code in self.termination_started_to_dict:
                self.termination_started_to_dict[code].company = company
                self.bulk_manager.add(self.termination_started_to_dict[code])
            if code in self.bancruptcy_readjustment_to_dict:
                self.bancruptcy_readjustment_to_dict[code].company = company
                self.bulk_manager.add(self.bancruptcy_readjustment_to_dict[code])
        self.bulk_manager.commit(Founder)
        self.bulk_manager.commit(Signer)
        self.bulk_manager.commit(Assignee)
        self.bulk_manager.commit(CompanyToPredecessor)
        self.bulk_manager.commit(ExchangeDataCompany)
        self.bulk_manager.commit(CompanyToKved)
        self.bulk_manager.commit(CompanyDetail)
        self.bulk_manager.commit(TerminationStarted)
        self.bulk_manager.commit(BancruptcyReadjustment)
        self.bulk_manager.queues['business_register.Company'] = []
        self.bulk_manager.queues['business_register.Founder'] = []
        self.bulk_manager.queues['business_register.Signer'] = []
        self.bulk_manager.queues['business_register.Assignee'] = []
        self.bulk_manager.queues['business_register.CompanyToPredecessor'] = []
        self.bulk_manager.queues['business_register.ExchangeDataCompany'] = []
        self.bulk_manager.queues['business_register.CompanyToKved'] = []
        self.bulk_manager.queues['business_register.CompanyDetail'] = []
        self.bulk_manager.queues['business_register.TerminationStarted'] = []
        self.bulk_manager.queues['business_register.BancruptcyReadjustment'] = []
        self.founder_to_dict = {}
        self.company_detail_to_dict = {}
        self.company_to_kved_to_dict = {}
        self.signer_to_dict = {}
        self.termination_started_to_dict = {}
        self.bancruptcy_readjustment_to_dict = {}
        self.company_to_predecessor_to_dict = {}
        self.assignee_to_dict = {}
        self.exchange_data_to_dict = {}
        self.time_it('save others\t\t')

    def delete_outdated(self):
        outdated_companies = list(set(self.already_stored_companies) - set(self.uptodated_companies))
        for company_id in outdated_companies:
            if CompanyDetail.objects.filter(company_id=company_id).first():
                CompanyDetail.objects.filter(company_id=company_id).first().soft_delete()
            if CompanyToPredecessor.objects.filter(company_id=company_id).first():
                CompanyToPredecessor.objects.filter(company_id=company_id).first().soft_delete()
            if TerminationStarted.objects.filter(company_id=company_id).first():
                TerminationStarted.objects.filter(company_id=company_id).first().soft_delete()
            if BancruptcyReadjustment.objects.filter(company_id=company_id).first():
                BancruptcyReadjustment.objects.filter(company_id=company_id).first().soft_delete()
            outdated_founders = list(Founder.objects.filter(company_id=company_id))
            if len(outdated_founders):
                for founder in outdated_founders:
                    founder.soft_delete()
            outdated_signers = list(Signer.objects.filter(company_id=company_id))
            if len(outdated_signers):
                for signer in outdated_signers:
                    signer.soft_delete()
            outdated_assignees = list(Assignee.objects.filter(company_id=company_id))
            if len(outdated_assignees):
                for assignee in outdated_assignees:
                    assignee.soft_delete()
            outdated_exchange_data = list(ExchangeDataCompany.objects.filter(company_id=company_id))
            if len(outdated_exchange_data):
                for exchange_data in outdated_exchange_data:
                    exchange_data.soft_delete()
            outdated_company_to_kved = list(CompanyToKved.objects.filter(company_id=company_id))
            if len(outdated_company_to_kved):
                for company_to_kved in outdated_company_to_kved:
                    company_to_kved.soft_delete()
            Company.objects.get(id=company_id).soft_delete()


class UkrCompanyFullDownloader(Downloader):
    chunk_size = 16 * 1024 * 1024
    reg_name = 'business_ukr_company'
    zip_required_file_sign = 'ufop_full'
    unzip_required_file_sign = 'EDR_UO_FULL'
    unzip_after_download = True
    source_dataset_url = settings.BUSINESS_UKR_COMPANY_SOURCE_PACKAGE
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_FULL

    def get_source_file_url(self):

        r = requests.get(self.source_dataset_url)
        if r.status_code != 200:
            print(f'Request error to {self.source_dataset_url}')
            return

        for i in r.json()['result']['resources']:
            # 17-ufop_25-11-2020.zip
            # 17-ufop_full_07-08-2020.zip  <---
            if self.zip_required_file_sign in i['url']:
                return i['url']

    def get_source_file_name(self):
        return self.url.split('/')[-1]

    def remove_unreadable_characters(self):
        file = self.local_path + self.LOCAL_FILE_NAME
        logger.info(f'{self.reg_name}: remove_unreadable_characters for {file} started ...')
        tmp = tempfile.mkstemp()
        with codecs.open(file, 'r', 'Windows-1251') as fd1, codecs.open(tmp[1], 'w', 'UTF-8') as fd2:
            for line in fd1:
                line = line.replace('&quot;', '"')\
                    .replace('windows-1251', 'UTF-8')\
                    .replace('&#3;', '')\
                    .replace('&#30;', '')
                fd2.write(line)
        os.rename(tmp[1], file)
        logger.info(f'{self.reg_name}: remove_unreadable_characters finished.')

    def update(self):

        logger.info(f'{self.reg_name}: Update started...')

        self.report_init()
        self.download()

        self.LOCAL_FILE_NAME = self.file_name
        self.remove_unreadable_characters()

        self.report.update_start = timezone.now()
        self.report.save()

        logger.info(f'{self.reg_name}: process() with {self.file_path} started ...')
        ukr_company_full = UkrCompanyFullConverter()
        ukr_company_full.LOCAL_FILE_NAME = self.file_name

        sleep(5)
        ukr_company_full.process()
        logger.info(f'{self.reg_name}: process() with {self.file_path} finished successfully.')

        self.report.update_finish = timezone.now()
        self.report.update_status = True
        self.report.save()

        sleep(5)
        self.vacuum_analyze(table_list=['business_register_company', ])

        self.remove_file()
        endpoints_cache_warm_up(endpoints=[
            '/api/company/',
            '/api/company/uk/',
            '/api/company/ukr/',
        ])
        new_total_records = Company.objects.filter(source=Company.UKRAINE_REGISTER).count()
        self.update_register_field(settings.UKR_COMPANY_REGISTER_LIST, 'total_records', new_total_records)
        logger.info(f'{self.reg_name}: Update total records finished successfully.')

        self.measure_company_changes(Company.UKRAINE_REGISTER)
        logger.info(f'{self.reg_name}: Report created successfully.')

        logger.info(f'{self.reg_name}: Update finished successfully.')
