from lxml import etree

from business_register.converter.business_converter import BusinessConverter
from business_register.models.company_models import Company, FounderNew


class FoundersUpdater(BusinessConverter):
    LOCAL_FILE_NAME = '../unzipped_xml/ltds_1.xml'
    CHUNK_SIZE = 100
    record = []
    
    # def __init__(self):
    #     self.all_companies_dict = self.put_all_objects_to_dict('name', 'business_register', 
    #                                                             "Company")
        
        # super().__init__()

    def parse_file(self):
        i = 0
        records = etree.Element('RECORDS')
        for _, elem in etree.iterparse(self.LOCAL_FILE_NAME, tag = 'DATA_RECORD'):           
            if len(records) < self.CHUNK_SIZE:
                records.append(elem)
            else:
                self.add_founders_info(records)
                records.clear()
            i += 1
            print(f'N{i}')
        print('All the records checked')


    def add_founders_info(self, records):
        j = 0
        for record in records:
            company_edrpou = record.xpath('EDRPOU')[0].text
            if not company_edrpou:
                return
            company = Company.objects.filter(edrpou=company_edrpou).first()
            if not company:
                return
            founder_name = record.xpath('FOUNDER_NAME')[0].text
            if not founder_name:
                return
            founder_info = record.xpath('FOUNDER_CODE')
            if not founder_info:
                return
            founder_code = founder_info[0].text
            # ignoring personal data according to the law 
            founder_edrpou = founder_code if len(founder_code) == 8 else None
            founder_equity = record.xpath('FOUNDER_EQUITY')[0].text
            if founder_equity:
                founder_equity = float(founder_equity.replace(',', '.'))
            founder_new = FounderNew(name=founder_name, edrpou=founder_edrpou, 
            equity=founder_equity, company=company)
            founder_new.save()
            j += 1

FoundersUpdater().parse_file()
