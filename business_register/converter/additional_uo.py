from lxml import etree

from business_register.converter.business_converter import BusinessConverter
from business_register.models.company_models import Company, FounderNew, FounderFull

def add_founders_info(records):
    for record in records:
        company_edrpou_info = record.xpath('EDRPOU')
        if not company_edrpou_info:
            return
        company_edrpou = company_edrpou_info[0].text
        if not company_edrpou:
            return
        company = Company.objects.filter(edrpou=company_edrpou).first()
        if not company:
            return
        founder_name_info = record.xpath('FOUNDER_NAME')
        if not founder_name_info:
            return
        founder_name = founder_name_info[0].text
        if not founder_name:
            return
        founder_code = None
        founder_code_info = record.xpath('FOUNDER_CODE')
        if founder_code_info:
            founder_code = founder_code_info[0].text
        founder_edrpou = None
        # ignoring personal data according to the law
        if founder_code and len(founder_code) == 8:
            founder_edrpou = founder_code
        founder_equity = None
        founder_equity_info = record.xpath('FOUNDER_EQUITY')
        if founder_equity_info:
            founder_equity = founder_equity_info[0].text
        if founder_equity:
            founder_equity = float(founder_equity.replace(',', '.'))
        if FounderNew.objects.filter(name=founder_name, company=company).first():
            continue
        else:
            founder_new = FounderNew(name=founder_name, edrpou=founder_edrpou,
                                     equity=founder_equity, company=company)
            founder_new.save()


class FoundersUpdater(BusinessConverter):
    LOCAL_FILE_NAME = ''
    CHUNK_SIZE = 500
    RECORD_TAG = 'DATA_RECORD'
    record = []

    def parse_file(self):
        i = 0
        records = etree.Element('RECORDS')
        for _, elem in etree.iterparse(self.LOCAL_FILE_NAME, tag=self.RECORD_TAG, recover=True):
            if len(records) < self.CHUNK_SIZE:
                records.append(elem)
            else:
                add_founders_info(records)
                records.clear()
            i += 1
            print(f'N{i}')
        print('All the records checked')
