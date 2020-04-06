import config
from ratu.models.ruo_models import Founders, Kved, Ruo, Stateruo
from ratu.services.main import Converter

class RuoConverter(Converter):
    
    #paths for remote and local source files
    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_RUO
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
        Founders,
        Kved,
        Ruo,
        Stateruo      
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

    #creating list for registration items that had writed to db
    state_list=[]
    kved_list=[]
    
    #writing entry to db 
    def save_to_db(self, record):
        state_ruo=self.save_to_state_ruo_table(record)
        kved=self.save_to_kved_table(record)
        ruo=self.save_to_ruo_table(record, state_ruo, kved)
        self.save_to_founders_table(record, ruo)
        print('saved')
        
    #writing entry to state_ruo table       
    def save_to_state_ruo_table(self, record):
        if record['STAN']:
            state_name=record['STAN']
        else:
            state_name=Stateruo.EMPTY_FIELD
        if not state_name in self.state_list:
            state_ruo = Stateruo(
                name=state_name
                )
            state_ruo.save()
            self.state_list.insert(0, state_name)
        state_ruo=Stateruo.objects.get(
            name=state_name
            )
        return state_ruo
    
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
    
    #writing entry to ruo table
    def save_to_ruo_table(self, record, state_ruo, kved):
        ruo = Ruo.objects.filter(
            state=state_ruo.id,
            kved=kved.id,
            name=record['NAME'],
            short_name=record['SHORT_NAME'],
            edrpou=record['EDRPOU'],
            address=record['ADDRESS'],
            boss=record['BOSS']  
        )
        if ruo.exists():  
            return ruo
        ruo = Ruo(
            state=state_ruo,
            kved=kved,
            name=record['NAME'],
            short_name=record['SHORT_NAME'],
            edrpou=record['EDRPOU'],
            address=record['ADDRESS'],
            boss=record['BOSS'] 
        )
        ruo.save()
       
        return ruo

    #writing entry to founder table
    def save_to_founders_table(self, record, ruo):            
        for founder in record['FOUNDER']:
            founders = Founders(
                company=ruo,
                founder=founder
            )
            founders.save()    
        
    print(
        'Ruo already imported. For start rewriting RUO to the DB run > RuoConverter().process()\n',
        'For clear RUO tables run > RuoConverter().clear_db()'
        )