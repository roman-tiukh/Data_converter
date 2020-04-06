import config
from ratu.models.rfop_models import Rfop, Staterfop
from ratu.models.ruo_models import Kved
from ratu.services.main import Converter

class RfopConverter(Converter):
    
    #paths for remote and local source files
    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_RFOP
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
        Kved,
        Rfop,
        Staterfop
    ]
    
    #format record's data
    record={
        'RECORD': '',
        'FIO': '',
        'ADDRESS': '',
        'KVED': '',
        'STAN': ''
    }
    
    #creating list for registration items that had writed to db
    state_list=[]
    kved_list=[]
    
    #writing entry to db 
    def save_to_db(self, record):
        state_rfop=self.save_to_state_rfop_table(record)
        kved=self.save_to_kved_table(record)
        self.save_to_rfop_table(record, state_rfop, kved)
        print('saved')
        
    #writing entry to state_rfop table       
    def save_to_state_rfop_table(self, record):
        if record['STAN']:
            state_name=record['STAN']
        else:
            state_name=Staterfop.EMPTY_FIELD
        if not state_name in self.state_list:
            state_rfop = Staterfop(
                name=state_name
                )
            state_rfop.save()
            self.state_list.insert(0, state_name)
        state_rfop=Staterfop.objects.get(
            name=state_name
            )
        return state_rfop
    
    #writing entry to kved table       
    def save_to_kved_table(self, record):
        if record['KVED']:
            kved_name=record['KVED']
        else:
            kved_name=Kved.EMPTY_FIELD
        if not kved_name in self.kved_list:
            kved = Kved(
                name=kved_name
                )
            kved.save()
            self.kved_list.insert(0, kved_name)
        kved=Kved.objects.get(
            name=kved_name
            )
        return kved
    
    #writing entry to rfop table
    def save_to_rfop_table(self, record, state_rfop, kved):
        rfop = Rfop(
            state=state_rfop,
            kved=kved,
            fullname=record['FIO'],
            address=record['ADDRESS']
            )
        rfop.save()
    
    print(
        'Rfop_class already imported. For start rewriting RFOP to the DB run > RfopConverter().process()\n',
        'For clear RFOP tables run > RfopConverter().clear_db()'
        )