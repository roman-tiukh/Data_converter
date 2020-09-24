import logging
from lxml import html
import requests
from django.utils import timezone
from csv import DictReader

from business_register.converter.company_converters.company import CompanyConverter
from business_register.models.company_models import Company
from data_ocean.utils import format_date_to_yymmdd, convert_to_string_if_exists
from location_register.converter.address import AddressConverter

from data_ocean.downloader import Downloader
from requests.auth import HTTPBasicAuth
from django.conf import settings

# Standard instance of a logger with __name__
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UkCompanyConverter(CompanyConverter):

    # def get_company_from_uk_register(self, number):
    #     AUTH = HTTPBasicAuth(
    #         'iegorsoboliev@dataocean.us', 'rQVkFwfb8AX2Cbdlohvc0pzPwfzholqPbBbIoR2W')
    #     url = f'https://api.companieshouse.gov.uk/company/{number}'
    #     with requests.get(url, stream=True, auth=AUTH) as response:
    #         data = response.json()
    #         print(data)

    def save_to_db(self, file):
        with open(file, newline='') as csvfile:
            for row in DictReader(csvfile):
                name = row['CompanyName'].lower()
                number = row[' CompanyNumber']
                code = name + number
                country = AddressConverter().save_or_get_country(row['CountryOfOrigin'])
                address = (
                    f"{row['RegAddress.Country']} {row['RegAddress.PostCode']} "
                    f"{row['RegAddress.County']} {row['RegAddress.PostTown']} "
                    f"{row[' RegAddress.AddressLine2']} {row['RegAddress.AddressLine1']} "
                    f"{row['RegAddress.POBox']} {row['RegAddress.CareOf']}"
                )
                company_type = self.save_or_get_company_type(row['CompanyCategory'], 'en')
                status = self.save_or_get_status(row['CompanyStatus'])
                registration_date = format_date_to_yymmdd(row['IncorporationDate'])
                company = Company.objects.filter(edrpou=number).first()
                if not company:
                    company = Company(
                        name=name,
                        company_type=company_type,
                        edrpou=number,
                        address=address,
                        country=country,
                        status=status,
                        registration_date=registration_date,
                        code=code
                    )
                    company.save()
                else:
                    update_fields = []
                    if company.name != name:
                        company.name = name
                        update_fields.append('name')
                    if company.company_type != company_type:
                        company.company_type = company_type
                        update_fields.append('company_type')
                    if company.address != address:
                        company.address = address
                        update_fields.append('address')
                    if company.country != country:
                        company.country = country
                        update_fields.append('country')
                    if company.status != status:
                        company.status = status
                        update_fields.append('status')
                    if convert_to_string_if_exists(company.registration_date) != registration_date:
                        company.registration_date = registration_date
                        update_fields.append('registration_date')
                    if company.code != code:
                        company.code = code
                        update_fields.append('code')

                    if update_fields:
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

        self.log_init()
        self.download()

        self.log_obj.update_start = timezone.now()
        self.log_obj.save()

        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) started ...')
        UkCompanyConverter().save_to_db(self.file_path)
        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) finished successfully.')

        self.log_obj.update_finish = timezone.now()
        self.log_obj.update_status = True
        self.log_obj.save()

        self.remove_file()

        logger.info(f'{self.reg_name}: Update finished successfully.')
