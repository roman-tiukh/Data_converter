import datetime
from django.apps import apps
from django.utils.dateparse import parse_date
from lxml import etree

from data_converter import settings_local
from data_ocean.converter import Converter, BulkCreateUpdateManager
from data_ocean.models import Authority
from business_register.models.company_models import Bylaw, Company, CompanyType, FounderFull
from data_ocean.models import Status

class Parser(Converter):
    LOCAL_FILE_NAME = settings_local.LOCAL_FILE_NAME_UO
    LOCAL_FOLDER = settings_local.LOCAL_FOLDER
    CHUNK_SIZE = 1000
    all_bylaw_dict = {}
    all_company_type_dict = {}
    company_update_dict = {}
    company_create_dict = {}  
    tables= [
        # Bylaw,
        Company,
        # CompanyType,
        FounderFull,
        # Status,
        # Authority
    ]
    bulk_manager = BulkCreateUpdateManager(100000)       
    
    def __init__(self):
        self.all_bylaw_dict = self.initialize_objects_for("business_register", "Bylaw")
        self.all_company_type_dict = self.initialize_objects_for("business_register", "CompanyType")
        
        super().__init__()

    def save_or_get_bylaw(self, record):
        if not record.xpath('STATUTE')[0].text in self.all_bylaw_dict:
            self.bylaw = Bylaw(name=record.xpath('STATUTE')[0].text)
            self.bylaw.save()
            self.all_bylaw_dict[record.xpath('STATUTE')[0].text] = self.bylaw   
        else:
            self.bylaw = self.all_bylaw_dict[record.xpath('STATUTE')[0].text]

    def save_or_get_company_type(self, record):                
        if not record.xpath('OPF')[0].text in self.all_company_type_dict:
            self.company_type = CompanyType(name=record.xpath('OPF')[0].text)
            self.company_type.save()
            self.all_company_type_dict[record.xpath('OPF')[0].text] = self.company_type   
        else:
            self.company_type = self.all_company_type_dict[record.xpath('OPF')[0].text]

    def create_hash_code(self, record, edrpou):
        hash_code = record.xpath('NAME')[0].text + edrpou
        return hash_code

    def company_create (self, record, edrpou, registration_date, registration_info):
        company = Company()
        company.name = record.xpath('NAME')[0].text
        company.short_name = record.xpath('SHORT_NAME')[0].text
        company.company_type = self.company_type
        
        company.edrpou = edrpou
        company.address = record.xpath('ADDRESS')[0].text
        company.status = self.status
        company.bylaw = self.bylaw
        company.registration_date = registration_date
        company.registration_info = registration_info
        company.contact_info = record.xpath('CONTACTS')[0].text
        company.authority = self.authority
        company.hash_code = self.create_hash_code(record, edrpou)
        return company

    def add_founders(self, record, edrpou):
        if len(record.xpath('FOUNDERS')[0]):
            for item in record.xpath('FOUNDERS')[0]:
                founder = FounderFull()
                founder.name = item.text
                founder.hash_code = self.create_hash_code(record, edrpou)
                self.bulk_manager.add_create(founder)
            
    def save_to_db(self, records):
        self.bylaw = None
        self.company_type = None
        for record in records:
            self.authority = self.save_or_get_authority(record.xpath('CURRENT_AUTHORITY')[0].text)
            self.status = self.save_or_get_status(record.xpath('STAN')[0].text)
            self.save_or_get_bylaw(record)
            self.save_or_get_company_type(record)

            edrpou = record.xpath('EDRPOU')[0].text or 'empty'
            registration_date = None
            registration_info = None
            registration = record.xpath('REGISTRATION')[0].text
            if registration:
                registration_date = self.format_date_to_yymmdd(self.get_first_word(registration)) or None
                registration_info = self.cut_first_word(registration) or None
            try:
                company = Company.objects.filter(hash_code = self.create_hash_code(record, edrpou)).first()
                company.short_name = record.xpath('SHORT_NAME')[0].text
                company.company_type = self.company_type
                company.address = record.xpath('ADDRESS')[0].text
                company.status = self.status
                company.bylaw = self.bylaw
                company.registration_date = registration_date
                company.registration_info = registration_info
                company.contact_info = record.xpath('CONTACTS')[0].text
                company.authority = self.authority
                self.bulk_manager.add_update(company)
                
                print('update')
            except:
                
                company = self.company_create(record, edrpou, registration_date, registration_info)
                self.bulk_manager.add_create(company)
                
                print('create')
            self.add_founders(record, edrpou)

        if len(self.bulk_manager._update_queues['business_register.Company']) > 0:

            # print(self.bulk_manager._update_queues['business_register.Company'])
            # print(self.bulk_manager._update_queues['business_register.Company'][0].pk)

            self.bulk_manager._commit_update(Company, ['name', 'short_name', 'company_type', 'edrpou'])
        
        
        self.bulk_manager._commit_create(Company)
        company_update_dict = {}
        company_create_dict = {}

        for company in self.bulk_manager._update_queues['business_register.Company']:
            company_update_dict[company.hash_code] = company
        for company in self.bulk_manager._create_queues['business_register.Company']:
            company_create_dict[company.hash_code] = company

        # self.bulk_manager._update_queues['business_register.Company'] = []
        # self.bulk_manager._create_queues['business_register.Company'] = []

        for founder in self.bulk_manager._create_queues['business_register.FounderFull']:
            if founder.hash_code in company_update_dict:
                founder.company = company_update_dict[founder.hash_code]

            else:
                founder.company = company_create_dict[founder.hash_code]

        self.bulk_manager._commit_create(FounderFull)
        self.bulk_manager._create_queues['business_register.FounderFull'] = []
