import config
from ratu.models.ruo_models import Founders, Kved, Ruo, State
from ratu.services.main import Converter, BulkCreateManager
from ratu.models.kzed_models import Kzed, Group, Division, Section

class RuoConverter(Converter):
    
    #paths for remote and local source files
    CHUNK_SIZE = 300
    FILE_URL = ""
    LOCAL_FILE_NAME = "uo.xml"
    
    #list of models for clearing DB
    tables=[
        Founders,
        Ruo,     
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

    def unzip_file(self): # empty function, because unzipping process executes in rfop module
        return

    #creating dictionaries for registration items that had writed to db
    state_dict={} # dictionary uses for keeping whole model class objects
    kved_dict={}
    index=0 # index for entries in _create_queues[model_key] list
    kzed_dict={}

    #filling state & kved dictionaries with with existing db items
    for state in State.objects.all():
        state_dict[state.name]=state
    for kved in Kved.objects.all():
        kved_dict[kved.name]=kved
    for kzed in Kzed.objects.all():
        kzed_dict[kzed.code] = kzed


    #creating BulkCreateManager objects
    bulk_manager = BulkCreateManager(CHUNK_SIZE)
    bulk_submanager = BulkCreateManager(100000) #chunck size 100000 for never reach it
    
    #writing entry to db 
    def save_to_db(self, record):
        state=self.save_to_state_table(record)
        kved=self.save_to_kved_table(record)
        # kzed = self.get_kzed(record)
        ruo=self.save_to_ruo_table(record, state, kved)
        # self.save_to_founders_table(record, ruo)
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
            self.kved_dict[kved_name]=kved
            return kved
        kved=self.kved_dict[kved_name]
        return kved
    
    #writing entry to kzed table       
    def get_kzed(self, record):
        if record['KVED']:
            record_as_list = record['KVED'].split(" ")
            kved_code=record_as_list[0]
        else:
            kved_code=Kzed.EMPTY_FIELD
        if kved_code not in kzed_dict:
            print (f"This kved doesn`t exist. Please, check {record['NAME']}")
            #toDo - insert EMPTY_KZED(section=Section.EMPTY_FIELD, division=Division.EMPTY_FIELD, 
            # group=Group.EMPTY_FIELD, code=Kzed.EMPTY_FIELD, name=Kzed.EMPTY_FIELD)
        return kzed_dict[kved_code]

    #writing entry to ruo & founders table
    def save_to_ruo_table(self, record, state, kved):
        ruo = Ruo.objects.filter(
            state=state.id,
            kved=kved.id,
            name=record['NAME'],
            short_name=record['SHORT_NAME'],
            edrpou=record['EDRPOU'],
            address=record['ADDRESS'],
            boss=record['BOSS']  
        )
        if ruo.exists():  
            return ruo.first()
        ruo = Ruo(
            state=state,
            kved=kved,
            name=record['NAME'],
            short_name=record['SHORT_NAME'],
            edrpou=record['EDRPOU'],
            address=record['ADDRESS'],
            boss=record['BOSS'] 
        )
        '''Для реализации метода bulk_create() при сохранении вложенных записей штатному полю id объекта founders
        временно присваивается значение индекса объекта ruo в списке _create_queues['ratu.Ruo']. После сохранения 
        в базе данных порции объектов ruo они получают свои уникальные id базы данных, после чего назначаются
        связанному полю founders.company в соответствии с временным id объекта founders. Далее поле founders.id 
        очищается от временного id для сохранения founders в базе данных с id назначенным базой'''
        self.bulk_manager.add(ruo)
        self.add_founders_to_queue(record, ruo)
        self.index = self.index+1
        if len(self.bulk_manager._create_queues['ratu.Ruo']) >= self.CHUNK_SIZE:
            for founders in self.bulk_submanager._create_queues['ratu.Founders']:
                founders.company =  self.bulk_manager._create_queues['ratu.Ruo'][founders.id]
                founders.id=None
            self.bulk_submanager._commit(Founders)
            self.bulk_submanager._create_queues['ratu.Founders']=[]
            self.index = 0

    #filling _create_queues['ratu.Founders'] list
    def add_founders_to_queue(self, record, ruo):        
        for founder in record['FOUNDER']:
            founders = Founders(
                id=self.index,
                company=ruo,
                founder=founder
            )
            self.bulk_submanager.add(founders)
        
    print(
        'Ruo already imported. For start rewriting RUO to the DB run > RuoConverter().process()\n',
        'For clear RUO tables run > RuoConverter().clear_db()'
        )
