import config
from ratu.models.rfop_models import Rfop, Staterfop
from ratu.models.ruo_models import Kved
from ratu.services.main import Converter
import time

class RfopConverter(Converter):
    
    #paths for remote and local source files
    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_RFOP
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
        #Kved,
        Rfop,
        #Staterfop
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
    state_dict={}
    kved_dict={}
    _create_queues=[]
    
    for state_rfop in Staterfop.objects.all():
        state_dict[state_rfop.name]=state_rfop
    for kved in Kved.objects.all():
        kved_dict[kved.name]=kved

    #writing entry to db 
    def save_to_db(self, record, parsing_time):
        state_rfop=self.save_to_state_rfop_table(record)
        state_rfop_time=time.time()
        print('saving in tables:\nstaterfop \t\t', round((state_rfop_time-parsing_time)*1000))
        kved=self.save_to_kved_table(record)
        kved_time=time.time()
        print('kved \t\t\t', round((kved_time-state_rfop_time)*1000))
        self.save_to_rfop_table(record, state_rfop, kved)
        rfop_time=time.time()
        print('rfop \t\t\t', round((rfop_time-kved_time)*1000))
        # print('saved')
        
    #writing entry to state_ruo table       
    def save_to_state_rfop_table(self, record):
        if record['STAN']:
            state_name=record['STAN']
        else:
            state_name=Staterfop.EMPTY_FIELD
        if not state_name in self.state_dict:
            state_rfop = Staterfop(
                name=state_name
                )
            state_rfop.save()
            #_create_queues.append(state_rfop)
            self.state_dict[state_name]=state_rfop
            return state_rfop
        state_rfop=self.state_dict[state_name]
        return state_rfop
    
    #writing entry to kved table       
    def save_to_kved_table(self, record):
        if record['KVED']:
            kved_name=record['KVED']
        else:
            kved_name=Kved.EMPTY_FIELD
        if not kved_name in self.kved_dict:
            kved = Kved(
                name=kved_name
                )
            kved.save()
            #_create_queues.append(kved)
            self.kved_dict[kved_name]=kved
            return kved
        kved=self.kved_dict[kved_name]
        return kved
    
    #writing entry to rfop table
    def save_to_rfop_table(self, record, state_rfop, kved):
        rfop = Rfop(
            state=state_rfop,
            kved=kved,
            fullname=record['FIO'],
            address=record['ADDRESS']
            )
        self._create_queues.append(rfop)
        #rfop.save()
        if len(self._create_queues) >= 200:
            Rfop.objects.bulk_create(self._create_queues)
            self._create_queues=[]
    
    print(
        'Rfop_class already imported. For start rewriting RFOP to the DB run > RfopConverter().process()\n',
        'For clear RFOP tables run > RfopConverter().clear_db()'
        )