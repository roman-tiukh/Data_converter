from business_register.models.kved_models import Kved
from business_register.models.ruo_models import Founders, Ruo, State
from data_ocean.converter import Converter, BulkCreateManager


class RuoConverter(Converter):
    CHUNK_SIZE = 300
    LOCAL_FILE_NAME = "uo.xml"
    DATASET_ID = "1c7f3815-3259-45e0-bdf1-64dca07ddc10"

    def rename_file(self, file):
        new_filename = file
        if (file.upper().find('UO') >= 0): new_filename = 'uo.xml'
        if (file.upper().find('FOP') >= 0): new_filename = 'fop.xml'
        return new_filename

    # list of models for clearing DB
    tables = [
        Founders,
        Ruo,
    ]

    # format record's data
    record = {
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

    # creating dictionaries for registration items that had writed to db
    state_dict = {}  # dictionary uses for keeping whole model class objects
    kved_dict = {}
    index = 0  # index for entries in _create_queues[model_key] list

    # filling state & kved dictionaries with with existing db items
    for state in State.objects.all():
        state_dict[state.name] = state
    for kved in Kved.objects.all():
        kved_dict[kved.code] = kved

    # creating BulkCreateManager objects
    bulk_manager = BulkCreateManager(CHUNK_SIZE)
    bulk_submanager = BulkCreateManager(100000)  # chunck size 100000 for never reach it

    # writing entry to db
    def save_to_db(self, record):
        state = self.save_to_state_table(record)
        kved = self.get_kved_from_DB(record, 'NAME')
        self.save_to_ruo_table(record, state, kved)
        print('saved')

    # writing entry to state table
    def save_to_state_table(self, record):
        if record['STAN']:
            state_name = record['STAN']
        else:
            state_name = State.EMPTY_FIELD
        if not state_name in self.state_dict:
            state = State(
                name=state_name
            )
            state.save()
            self.state_dict[state_name] = state
            return state
        state = self.state_dict[state_name]
        return state

    # writing entry to ruo & founders table
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
        self.index = self.index + 1
        if len(self.bulk_manager._create_queues['data_ocean.Ruo']) >= self.CHUNK_SIZE:
            for founders in self.bulk_submanager._create_queues['data_ocean.Founders']:
                founders.company = self.bulk_manager._create_queues['data_ocean.Ruo'][founders.id]
                founders.id = None
            self.bulk_submanager._commit(Founders)
            self.bulk_submanager._create_queues['data_ocean.Founders'] = []
            self.index = 0

    # filling _create_queues['ratu.Founders'] list
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