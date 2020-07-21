import datetime
from django.apps import apps
from django.conf import settings

from business_register.constants import HistoryTypes
from business_register.models.company_models import Company, CompanyDetail, Signer
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
            company.history_type = HistoryTypes.UPDATE
            company.code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
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
            signer.history_type = HistoryTypes.UPDATE
            signer.code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
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
            founder.history_type = HistoryTypes.UPDATE
            founder.code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            founder.created_at = datetime.datetime.now()
            self.create_queues.append(founder)
        self.HistoricalFounderFull.objects.bulk_create(self.create_queues)
        self.create_queues = []


class NameHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_NAME
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
            company.name = record.xpath('NAME')[0].text
            company.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                company_exists = Company.objects.filter(edrpou=company.edrpou).first()
                company.id = company_exists.id
            except AttributeError:
                company.id = 0 #for changed records that can't be assigned to existing company
            company.history_type = HistoryTypes.UPDATE
            company.code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            company.created_at = datetime.datetime.now()
            self.create_queues.append(company)
        self.HistoricalCompany.objects.bulk_create(self.create_queues)
        self.create_queues = []


class ShortNameHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_SHORTNAME
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
            if len(record.xpath('SHORT_NAME')) > 0:
                company.short_name = record.xpath('SHORT_NAME')[0].text
            else:
                company.short_name = ''
            company.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            name = ''
            try:
                company_exists = Company.objects.filter(edrpou=company.edrpou).first()
                company.id = company_exists.id
                name = company_exists.name
            except AttributeError:
                company.id = 0 #for changed records that can't be assigned to existing company
            company.history_type = HistoryTypes.UPDATE
            company.code = name + record.xpath('EDRPOU')[0].text
            company.created_at = datetime.datetime.now()
            self.create_queues.append(company)
        self.HistoricalCompany.objects.bulk_create(self.create_queues)
        self.create_queues = []


class CapitalHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_CAPITAL
    LOCAL_FOLDER = settings.LOCAL_FOLDER
    CHUNK_SIZE = 2000
    RECORD_TAG = 'DATA_RECORD'
    HistoricalCompanyDetail = apps.get_model('business_register', 'HistoricalCompanyDetail')
    tables = [HistoricalCompanyDetail]
    create_queues = []

    def save_to_db(self, records):
        for record in records:
            company_detail = self.HistoricalCompanyDetail()
            edrpou = record.xpath('EDRPOU')[0].text
            if len(record.xpath('AUTHORIZED_CAPITAL')) > 0:
                company_detail.authorized_capital = record.xpath('AUTHORIZED_CAPITAL')[0].text
            else:
                company_detail.authorized_capital = ''
            company_detail.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                company_exists = Company.objects.filter(edrpou=edrpou).first()
                company_detail.company = company_exists
            except AttributeError:
                continue
            try:
                company_detail.id = CompanyDetail.objects.filter(company=company_exists).first().id
            except AttributeError:
                company_detail.id = 0 #for changed records that can't be assigned
            company_detail.history_type = HistoryTypes.UPDATE
            company_detail.code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            company_detail.created_at = datetime.datetime.now()
            self.create_queues.append(company_detail)
        self.HistoricalCompanyDetail.objects.bulk_create(self.create_queues)
        self.create_queues = []


class BranchHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_BRANCH
    LOCAL_FOLDER = settings.LOCAL_FOLDER
    CHUNK_SIZE = 2000
    RECORD_TAG = 'DATA_RECORD'
    HistoricalCompany = apps.get_model('business_register', 'HistoricalCompany')
    tables = [HistoricalCompany]
    create_queues = []

    def save_to_db(self, records):
        for record in records:
            branch = self.HistoricalCompany()
            # branch.edrpou = record.xpath('')[0].text
            branch.name = record.xpath('BRANCH_NAME')[0].text
            if len (record.xpath('BRANCH_CODE')) > 0:
                branch.short_name = record.xpath('BRANCH_CODE')[0].text
            else:
                branch.short_name = ''
            branch.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                company_exists = Company.objects.filter(
                    edrpou=record.xpath('EDRPOU')[0].text).first()
                branch.id = company_exists.id
                branch.parent = company_exists
            except AttributeError:
                branch.id = 0 #for changed records that can't be assigned to existing company
            branch.history_type = HistoryTypes.UPDATE
            branch.code = record.xpath('BRANCH_NAME')[0].text + \
                                  branch.short_name
            branch.created_at = datetime.datetime.now()
            self.create_queues.append(branch)
        self.HistoricalCompany.objects.bulk_create(self.create_queues)
        self.create_queues = []


class InfoHistorical(Converter):
    LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_UO_INFO
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
            if len(record.xpath('PHONE_1')) > 0:
                phone_1 = record.xpath('PHONE_1')[0].text
            else:
                phone_1 = ''
            if len(record.xpath('PHONE_2')) > 0:
                phone_2 = record.xpath('PHONE_2')[0].text
            else:
                phone_2 = ''
            if len(record.xpath('FAX')) > 0:
                fax = record.xpath('FAX')[0].text
            else:
                fax = ''
            if len(record.xpath('EMAIL')) > 0:
                email = record.xpath('EMAIL')[0].text
            else:
                email = ''
            if len(record.xpath('WWW')) > 0:
                www = record.xpath('WWW')[0].text
            else:
                www = ''
            company.contact_info = (
                f'phone_1: {phone_1}; phone_2: {phone_2}; '
                f'fax: {fax}; email: {email}; www: {www}'
            )
            company.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                company_exists = Company.objects.filter(edrpou=company.edrpou).first()
                company.id = company_exists.id
            except AttributeError:
                company.id = 0 #for changed records that can't be assigned to existing company
            company.history_type = HistoryTypes.UPDATE
            company.code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            company.created_at = datetime.datetime.now()
            self.create_queues.append(company)
        self.HistoricalCompany.objects.bulk_create(self.create_queues)
        self.create_queues = []
