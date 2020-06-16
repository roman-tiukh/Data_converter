from lxml import etree

from business_register.converter.business_converter import BusinessConverter
from business_register.models.company_models import Company, FounderNew


class FoundersUpdater(BusinessConverter):
    LOCAL_FILE_NAME = '../Data_converter/unzipped_xml/ltds_1.xml'
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
            founder_code_info = record.xpath('FOUNDER_CODE')
            if founder_code_info:
                founder_code = founder_code_info[0].text
            else:
                founder_code = None
            # ignoring personal data according to the law 
            if founder_code and len(founder_code) == 8:
                founder_edrpou = founder_code
            else:
                founder_edrpou = None
            founder_equity_info = record.xpath('FOUNDER_EQUITY')
            if founder_equity_info:
                founder_equity = founder_equity_info[0].text
            if founder_equity:
                founder_equity = float(founder_equity.replace(',', '.'))
            else:
                founder_equity = None
            founder_new = FounderNew(name=founder_name, edrpou=founder_edrpou, 
            equity=founder_equity, company=company)
            founder_new.save()

FoundersUpdater().parse_file()
