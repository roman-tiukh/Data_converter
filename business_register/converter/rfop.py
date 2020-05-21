from business_register.models.kved_models import Kved
from business_register.models.rfop_models import Rfop
from business_register.models.ruo_models import State
from data_ocean.converter import Converter, BulkCreateManager


class RfopConverter(Converter):
    LOCAL_FILE_NAME = "fop.xml"
    DATASET_ID = "1c7f3815-3259-45e0-bdf1-64dca07ddc10"
    CHUNK_SIZE = 200

    def rename_file(self, file):
        new_filename = file
        if (file.upper().find('UO') >= 0): new_filename = 'uo.xml'
        if (file.upper().find('FOP') >= 0): new_filename = 'fop.xml'
        return new_filename

    # list of models for clearing DB
    tables = [
        Rfop
    ]

    # format record's data
    record = {
        'RECORD': '',
        'FIO': '',
        'ADDRESS': '',
        'KVED': '',
        'STAN': ''
    }

    # creating dictionaries for registration items that had writed to db
    state_dict = {}  # dictionary uses for keeping whole model class objects
    kved_dict = {}

    bulk_manager = BulkCreateManager(CHUNK_SIZE)

    for state in State.objects.all():
        state_dict[state.name] = state
    for kved in Kved.objects.all():
        kved_dict[kved.code] = kved

    # writing entry to db
    def save_to_db(self, record):
        state = self.save_to_state_table(record)
        kved = self.get_kved_from_DB(record, 'FIO')
        self.save_to_rfop_table(record, state, kved)
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

    # writing entry to rfop table
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