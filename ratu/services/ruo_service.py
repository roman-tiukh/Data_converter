import ratu.config as config
from ratu.models.ruo_models import Company, Founders
from ratu.services.main import Converter

class Ruo(Converter):
    
    #paths for remote and local sours files
    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_RUO
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
        Company,
        Founders
    ]
    
    #format record's data
    record={
        'RECORD': '',
        'NAME': '',
        'SHORT_NAME': '',
        'EDRPOU': '',
        'ADDRESS': '',
        'BOSS': '',
        'KVED': '',
        'STAN': '',
        'FOUNDING_DOCUMENT_NUM': '',
        'FOUNDERS': '',
        'FOUNDER': []
    }

    #writing entry to db
    def save_to_db(self, record):
        self.save_to_company_table(record)
        self.save_to_founders_table(record)
        print('saved')
    
    #writing entry to company table
    def save_to_company_table(self, record):           
        global company
        company = Company(
            name=record['NAME'],
            short_name=record['SHORT_NAME'],
            edrpou=record['EDRPOU'],
            address=record['ADDRESS'],
            boss=record['BOSS'],
            kved=record['KVED'],
            state=record['STAN']
            )
        company.save()
        company=Company.objects.get(
            name=company.name,
            edrpou=company.edrpou,
            kved=company.kved,
        )

    #writing entry to founder table
    def save_to_founders_table(self, record):            
        for founder in record['FOUNDER']:
            founders = Founders(
                company=company,
                founder=founder
            )
            founders.save()    
        
    print(
        'Ruo already imported. For start rewriting RUO to the DB run > Ruo().process()\n',
        'For clear "Company" and "Founders" tables run > Ruo().clear_db()'
        )