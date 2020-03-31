import ratu.config as config
from ratu.models.rfop_models import Rfop
from ratu.services import Converter

class Rfop_class(Converter):
    
    #paths for remote and local sours files
    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_RFOP
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
        Rfop
    ]
    
    #format record's data
    record={
        'RECORD': '',
        'FIO': '',
        'ADDRESS': '',
        'KVED': '',
        'STAN': ''
    }
     
    def save_to_db(self, record):
               
        #writing entry to region table
        rfop = Rfop(
            fullname=record['FIO'],
            address=record['ADDRESS'],
            kved=record['KVED'],
            state=record['STAN']
            )
        rfop.save()
    
        print('saved')
    print('Ratu already imported. For start rewriting to the DB run > Rfop_class().process()')