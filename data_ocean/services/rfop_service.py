import config
from data_ocean.models.rfop_models import Rfop
from data_ocean.models.ruo_models import State
from data_ocean.models.kved_models import Kved
from data_ocean.services.main import Converter, BulkCreateManager

class RfopConverter(Converter):
    
    #paths for remote and local source files
    # FILE_URL = "https://data.gov.ua/dataset/b244f35a-e50a-4a80-b704-032c42ba8142/resource/06bbccbd-e19c-40d5-9e18-447b110c0b4c/download/"
    # DOWNLOADED_FILE_NAME = "rfop_ruo.zip"
    # LOCAL_FILE_NAME = "fop.xml"
    DATASET_ID = "1c7f3815-3259-45e0-bdf1-64dca07ddc10"
    CHUNK_SIZE = 200

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
    
    def rename (self, file):
        new_filename = ""
        if (file.upper().find('UO') >= 0): new_filename = 'uo.xml'
        if (file.upper().find('FOP') >= 0): new_filename = 'fop.xml'
        return new_filename
        
    #creating dictionaries for registration items that had writed to db
    state_dict={} # dictionary uses for keeping whole model class objects
    kved_dict={}

    bulk_manager = BulkCreateManager(CHUNK_SIZE)
    
    for state in State.objects.all():
        state_dict[state.name]=state
    for kved in Kved.objects.all():
        kved_dict[kved.code]=kved

    #writing entry to db 
    def save_to_db(self, record):
        state=self.save_to_state_table(record)
        kved=self.get_kved_from_DB(record, 'FIO')
        self.save_to_rfop_table(record, state, kved)
        print('saved')
        
    #writing entry to state table       
    def save_to_state_table(self, record):
        if record['STAN']:
            state_name=record['STAN']
        else:
            state_name=State.EMPTY_FIELD
        if not state_name in self.state_dict:
            state = State(
                name=state_name
                )
            state.save()
            self.state_dict[state_name]=state
            return state
        state=self.state_dict[state_name]
        return state
                
    #writing entry to rfop table
    def save_to_rfop_table(self, record, state, kved):
        rfop = Rfop(
            state=state,
            kved=kved,
            fullname=record['FIO'],
            address=record['ADDRESS']
            )
        self.bulk_manager.add(rfop)

    print(
        'Rfop_class already imported. For start rewriting RFOP to the DB run > RfopConverter().process()\n',
        'For clear RFOP tables run > RfopConverter().clear_db()'
        )