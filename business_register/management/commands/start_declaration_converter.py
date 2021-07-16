from django.core.management import BaseCommand
from business_register.converter.declaration import DeclarationConverter
from business_register.models.pep_models import Pep
from business_register.pep_scoring.declarations_fixes import DeclarationsFixSet
from data_ocean.savepoint import Savepoint


class Command(BaseCommand):
    help = '---'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savepoint = Savepoint('declarations_savepoint')
        self.converter = DeclarationConverter()

    def add_arguments(self, parser):
        parser.add_argument('--pep_source_id', nargs='?', type=int)
        parser.add_argument('--pep_id', nargs='?', type=int)
        parser.add_argument('--declaration_id', nargs='?', type=str)

    def load_one(self, pep: Pep):
        for nacp_id in pep.nacp_id:
            self.converter.save_declarations_for_pep(nacp_declarant_id=nacp_id)

    def load_declaration(self, declaration_id: str):
        self.converter.save_one_declaration(declaration_id=declaration_id)

    def load_all(self):
        i = 0
        count = len(self.converter.only_peps)
        for nacp_declarant_id in self.converter.only_peps:
            i += 1
            self.stdout.write(f'\rProgress: {i} of {count}', ending='')
            self.stdout.flush()
            if not self.savepoint.has(nacp_declarant_id):
                self.converter.save_declarations_for_pep(nacp_declarant_id=nacp_declarant_id)
                self.savepoint.add(nacp_declarant_id)
        self.stdout.write()

    def handle(self, *args, **options):
        pep_source_id = options['pep_source_id']
        pep_id = options['pep_id']
        declaration_id = options['declaration_id']

        if pep_source_id:
            self.load_one(Pep.objects.get(source_id=pep_source_id))
        elif pep_id:
            self.load_one(Pep.objects.get(id=pep_id))
        elif declaration_id:
            self.load_declaration(declaration_id)
        else:
            self.load_all()

        self.stdout.write('Load done. Start running all fixes')
        DeclarationsFixSet().run_all_fixes()
        self.stdout.write('All fixes applied')
