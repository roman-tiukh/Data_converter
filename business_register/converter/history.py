import datetime
from django.apps import apps
from django.conf import settings

from business_register.models.company_models import Company, Signer
from data_ocean.converter import Converter


class AddressHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_ADDRESS
    LOCAL_FOLDER = settings.LOCAL_FOLDER
    CHUNK_SIZE = 2000
    RECORD_TAG = 'DATA_RECORD'
    HistoricalCompany = apps.get_model('business_register', 'HistoricalCompany')
    tables = [HistoricalCompany]
    create_queues = []

    def save_to_db(self, records):
        for record in records:
            company = self.HistoricalCompany()
            company.edrpou = record.xpath('EDRPOU')[0].text
            address = record.xpath('Address')[0].text
            company.address = " ".join(address.split())[:1000]
            company.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                company_exists = Company.objects.filter(edrpou=company.edrpou).first()
                company.id = company_exists.id
            except AttributeError:
                company.id = 0 #for changed records that can't be assigned to existing company
            company.history_type = '~'
            # django-simple-history history_type: + for create, ~ for update, and - for delete
            company.hash_code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            company.created_at = datetime.datetime.now()
            self.create_queues.append(company)
        self.HistoricalCompany.objects.bulk_create(self.create_queues)
        self.create_queues = []


class SignerHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_SIGNER
    LOCAL_FOLDER = settings.LOCAL_FOLDER
    CHUNK_SIZE = 2000
    RECORD_TAG = 'DATA_RECORD'
    HistoricalSigner = apps.get_model('business_register', 'HistoricalSigner')
    tables = [HistoricalSigner]
    create_queues = []

    def save_to_db(self, records):
        for record in records:
            signer = self.HistoricalSigner()
            edrpou = record.xpath('EDRPOU')[0].text
            signer.name = record.xpath('SIGNER')[0].text
            signer.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                company_exists = Company.objects.filter(edrpou=edrpou).first()
                signer.company = company_exists
            except AttributeError:
                continue
            try:
                signer.id = Signer.objects.filter(company=company_exists).first().id
            except AttributeError:
                signer.id = 0 #for changed records that can't be assigned to existing company
            signer.history_type = '~'
            # django-simple-history history_type: + for create, ~ for update, and - for delete
            signer.hash_code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            signer.created_at = datetime.datetime.now()
            self.create_queues.append(signer)
        self.HistoricalSigner.objects.bulk_create(self.create_queues)
        self.create_queues = []


class FounderHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_FOUNDER
    LOCAL_FOLDER = settings.LOCAL_FOLDER
    CHUNK_SIZE = 2000
    RECORD_TAG = 'DATA_RECORD'
    HistoricalFounderFull = apps.get_model('business_register', 'HistoricalFounderFull')
    tables = [HistoricalFounderFull]
    create_queues = []

    def save_to_db(self, records):
        for record in records:
            founder = self.HistoricalFounderFull()
            edrpou = record.xpath('EDRPOU')[0].text
            founder.name = record.xpath('FOUNDER')[0].text
            founder.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                company_exists = Company.objects.filter(edrpou=edrpou).first()
                founder.company = company_exists
            except AttributeError:
                continue
            try:
                founder.id = Signer.objects.filter(company=company_exists).first().id
            except AttributeError:
                founder.id = 0 #for changed records that can't be assigned to existing company
            founder.history_type = '~'
            # django-simple-history history_type: + for create, ~ for update, and - for delete
            founder.hash_code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            founder.created_at = datetime.datetime.now()
            self.create_queues.append(founder)
        self.HistoricalFounderFull.objects.bulk_create(self.create_queues)
        self.create_queues = []
