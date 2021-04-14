import logging
from csv import DictReader

import requests
from django.conf import settings
from django.utils import timezone
from lxml import html

from business_register.converter.company_converters.company import CompanyConverter
from business_register.models.company_models import Company
from data_ocean.downloader import Downloader
from data_ocean.utils import format_date_to_yymmdd, to_lower_string_if_exists

# Standard instance of a logger with __name__
from stats.tasks import endpoints_cache_warm_up

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UkCompanyConverter(CompanyConverter):

    def save_to_db(self, file):
        with open(file, newline='') as csvfile:
            index = 0

            for row in DictReader(csvfile):
                name = row['CompanyName'].lower()
                # number is unique identifier in Company House
                number = row[' CompanyNumber']
                code = name + number
                country = self.save_or_get_country(row['CountryOfOrigin'])
                address = (
                    f"{row['RegAddress.Country']} {row['RegAddress.PostCode']} "
                    f"{row['RegAddress.County']} {row['RegAddress.PostTown']} "
                    f"{row[' RegAddress.AddressLine2']} {row['RegAddress.AddressLine1']} "
                    f"{row['RegAddress.POBox']} {row['RegAddress.CareOf']}"
                )
                company_type = self.save_or_get_company_type(row['CompanyCategory'], 'en')
                status = self.save_or_get_status(row['CompanyStatus'])
                if len(row['IncorporationDate']) == 10:
                    registration_date = format_date_to_yymmdd(row['IncorporationDate'])
                else:
                    registration_date = None
                source = Company.GREAT_BRITAIN_REGISTER
                company = Company.objects.filter(edrpou=number, source=Company.GREAT_BRITAIN_REGISTER).first()
                if not company:
                    company = Company(
                        name=name,
                        company_type=company_type,
                        edrpou=number,
                        address=address,
                        country=country,
                        status=status,
                        registration_date=registration_date,
                        code=code,
                        source=source
                    )
                    company.save()
                else:
                    update_fields = []
                    if company.name != name:
                        company.name = name
                        update_fields.append('name')
                    if company.company_type_id != company_type.id:
                        company.company_type = company_type
                        update_fields.append('company_type')
                    if company.address != address:
                        company.address = address
                        update_fields.append('address')
                    if company.country_id != country.id:
                        company.country = country
                        update_fields.append('country')
                    if company.status_id != status.id:
                        company.status = status
                        update_fields.append('status')
                    if to_lower_string_if_exists(company.registration_date) != registration_date:
                        company.registration_date = registration_date
                        update_fields.append('registration_date')
                    if company.code != code:
                        company.code = code
                        update_fields.append('code')
                    if company.source != source:
                        company.source = source
                        update_fields.append('source')
                    if update_fields:
                        update_fields.append('updated_at')
                        company.save(update_fields=update_fields)

            print('All companies from UK register were saved')


class UkCompanyDownloader(Downloader):
    unzip_after_download = True
    unzip_required_file_sign = 'BasicCompanyDataAsOneFile'
    reg_name = 'business_uk_company'
    source_dataset_url = settings.BUSINESS_UK_COMPANY_SOURCE_PAGE

    def get_source_file_url(self):
        r = requests.get(self.source_dataset_url)
        if r.status_code != 200:
            print(f'Request error to {self.source_dataset_url}')
            return

        tree = html.fromstring(r.content)
        url = settings.BUSINESS_UK_COMPANY_SOURCE + tree.xpath(settings.BUSINESS_UK_COMPANY_SOURCE_XPATH)[0]
        return url

    def get_source_file_name(self):
        return self.url.split('/')[-1]

    def update(self):
        logger.info(f'{self.reg_name}: Update started...')

        self.report_init()
        self.download()

        self.report.update_start = timezone.now()
        self.report.save()

        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) started ...')
        UkCompanyConverter().save_to_db(self.file_path)
        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) finished successfully.')

        self.report.update_finish = timezone.now()
        self.report.update_status = True
        self.report.save()

        self.vacuum_analyze(table_list=['business_register_company', ])

        self.remove_file()
        endpoints_cache_warm_up(endpoints=[
            '/api/company/',
            '/api/company/uk/',
            '/api/company/ukr/',
        ])
        new_total_records = Company.objects.filter(source=Company.GREAT_BRITAIN_REGISTER).count()
        self.update_register_field(settings.UK_COMPANY_REGISTER_LIST, 'total_records', new_total_records)
        logger.info(f'{self.reg_name}: Update total records finished successfully.')

        self.measure_company_changes(Company.GREAT_BRITAIN_REGISTER)
        logger.info(f'{self.reg_name}: Report created successfully.')

        logger.info(f'{self.reg_name}: Update finished successfully.')
