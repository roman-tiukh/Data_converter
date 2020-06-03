import datetime
from django.apps import apps
from django.utils.dateparse import parse_date
from lxml import etree

from data_converter import settings_local
from data_ocean.converter import Converter, BulkCreateManager
from data_ocean.models import Authority
from business_register.models.company_models import Bylaw, Company, CompanyType, FounderFull
from data_ocean.models import Status

class Parser(Converter):
    LOCAL_FILE_NAME = settings_local.LOCAL_FILE_NAME_UO
    LOCAL_FOLDER = settings_local.LOCAL_FOLDER
    CHUNK_SIZE = 5
    all_bylaw_dict = {}
    all_company_type_dict = {}
    company_update_dict = {}
    company_create_dict = {}  
    tables= [
        # Bylaw,
        # Company,
        # CompanyType,
        FounderFull,
        # Status,
        # Authority
    ]
    bulk_manager = BulkCreateManager(100000)       
    bylaw = None
    company_type = None 
    
    def __init__(self):
        self.all_bylaw_dict = self.initialize_objects_for("business_register", "Bylaw")
        self.all_company_type_dict = self.initialize_objects_for("business_register", "CompanyType")
        
        super(Parser, self).__init__()

    def fill_foreign_tables(self, record):
        self.authority = self.save_or_get_authority(record.xpath('CURRENT_AUTHORITY')[0].text)
        self.status = self.save_or_get_status(record.xpath('STAN')[0].text)      
        
        if not record.xpath('STATUTE')[0].text in self.all_bylaw_dict:
            print(self.all_bylaw_dict)
            self.bylaw = Bylaw(name=record.xpath('STATUTE')[0].text)
            self.bylaw.save()
            self.all_bylaw_dict[record.xpath('STATUTE')[0].text] = self.bylaw   
        else:
            self.bylaw = self.all_bylaw_dict[record.xpath('STATUTE')[0].text]
                    
        if not record.xpath('OPF')[0].text in self.all_company_type_dict:
            print(self.all_company_type_dict)
            self.company_type = CompanyType(name=record.xpath('OPF')[0].text)
            self.company_type.save()
            self.all_company_type_dict[record.xpath('OPF')[0].text] = self.company_type   
        else:
            self.company_type = self.all_company_type_dict[record.xpath('OPF')[0].text]

    def company_create (self, record):
        company = Company()
        company.name = record.xpath('NAME')[0].text
        company.short_name = record.xpath('SHORT_NAME')[0].text
        company.company_type = self.company_type
        if record.xpath('EDRPOU')[0].text:
            company.edrpou = record.xpath('EDRPOU')[0].text
        else:
            company.edrpou = 'empty'
        company.address = record.xpath('ADDRESS')[0].text
        company.status = self.status
        company.bylaw = self.bylaw
        if record.xpath('REGISTRATION')[0].text:
            company.registration_date = self.format_date_to_yymmdd(self.get_first_word(record.xpath('REGISTRATION')[0].text))
            company.registration_info = self.cut_first_word(record.xpath('REGISTRATION')[0].text)
        company.contact_info = record.xpath('CONTACTS')[0].text
        company.authority = self.authority
        company.hash_code = record.xpath('NAME')[0].text + company.edrpou
        return company

    def add_founders(self, record, edrpou):
        if len(record.xpath('FOUNDERS')[0]):
            for item in record.xpath('FOUNDERS')[0]:
                founder = FounderFull()
                founder.name = item.text
                founder.hash_code = record.xpath('NAME')[0].text + edrpou
                self.bulk_manager.add_create(founder)
            
    def save_to_db(self, records):
        for record in records:
            self.fill_foreign_tables(record)
            if record.xpath('EDRPOU')[0].text:
                edrpou = record.xpath('EDRPOU')[0].text
            else:
                edrpou = 'empty'
            registration_date = None
            registration_info = None
            if record.xpath('REGISTRATION')[0].text:
                    registration_date = self.format_date_to_yymmdd(self.get_first_word(record.xpath('REGISTRATION')[0].text))
                    registration_info = self.cut_first_word(record.xpath('REGISTRATION')[0].text)
            company_list = Company.objects.filter(
                name = record.xpath('NAME')[0].text,
                short_name = record.xpath('SHORT_NAME')[0].text,
                company_type = self.company_type,
                edrpou = edrpou,
                address = record.xpath('ADDRESS')[0].text,
                status = self.status,
                bylaw = self.bylaw,
                registration_date = registration_date,
                registration_info = registration_info,
                contact_info = record.xpath('CONTACTS')[0].text,
                authority = self.authority,
                hash_code = record.xpath('NAME')[0].text + edrpou
            )
            if company_list.exists():
                company = company_list.first()
                self.bulk_manager.add_update(company)
                self.add_founders(record, edrpou)
            else:
                
                company = self.company_create(record)
                self.bulk_manager.add_create(company)
                self.add_founders(record, edrpou)
        try:
            self.bulk_manager._commit_update(Company, ['name', 'short_name', 'company_type', 'edrpou'])
        except:
            None
        
        self.bulk_manager._commit_create(Company)
        company_update_dict = {}
        company_create_dict = {}

        for company in self.bulk_manager._update_queues['business_register.Company']:
            company_update_dict[company.hash_code] = company
        for company in self.bulk_manager._create_queues['business_register.Company']:
            company_create_dict[company.hash_code] = company

        for founder in self.bulk_manager._create_queues['business_register.FounderFull']:
            if founder.hash_code in company_update_dict:
                founder.company = company_update_dict[founder.hash_code]

            else:
                founder.company = company_create_dict[founder.hash_code]

        self.bulk_manager._commit_create(FounderFull)
        self.bulk_manager._create_queues['business_register.FounderFull']=[]
