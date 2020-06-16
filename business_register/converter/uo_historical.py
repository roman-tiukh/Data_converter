import datetime
from django.apps import apps

from business_register.models.company_models import Company
from data_converter import settings_local
from data_ocean.converter import Converter


class Historical(Converter):
    LOCAL_FILE_NAME = settings_local.LOCAL_FILE_NAME_UO_ADDRESS
    LOCAL_FOLDER = settings_local.LOCAL_FOLDER
    CHUNK_SIZE = 500
    HistoricalCompany = apps.get_model('business_register', 'HistoricalCompany')
    tables = [HistoricalCompany]
    create_queues = []

    def save_to_db(self, records):
        for record in records:
            company = self.HistoricalCompany()
            company.edrpou = record.xpath('EDRPOU')[0].text
            company.address = record.xpath('Address')[0].text
            company.history_date = datetime.datetime.strptime(
                record.xpath('DATE')[0].text,
                "%Y/%m/%d %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            if Company.objects.filter(edrpou=company.edrpou).first():
                company.id = Company.objects.filter(edrpou=company.edrpou).first().id
            else:
                company.id = 0 #for changed records that can't be assigned to existing company
            company.history_type = '~'
            company.hash_code = record.xpath('NAME')[0].text + record.xpath('EDRPOU')[0].text
            company.created_at = datetime.datetime.now()
            self.create_queues.append(company)
        self.HistoricalCompany.objects.bulk_create(self.create_queues)
        self.create_queues = []
