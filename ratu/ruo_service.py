import ratu.config as config
from ratu.models.ruo_models import Company, Founders
from ratu.services import Converter

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
     
    def save_to_db(self, record):
               
        #writing entry to company table
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
                
        #writing entry to founder table
        for founder in record['FOUNDER']:
            founders = Founders(
                company=company.id,
                founder=founder
            )
            founders.save()
        print('saved')
    print('Ruo already imported. For start rewriting to the DB run > Ruo().process()')