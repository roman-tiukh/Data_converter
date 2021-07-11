import os

from django.conf import settings
from django.core.management import BaseCommand
from business_register.converter.declaration import DeclarationConverter
from business_register.models.pep_models import Pep


class Command(BaseCommand):
    help = '---'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.savepoint_file_path = os.path.join(settings.BASE_DIR, 'export', 'declarations_savepoint.txt')
        self.peps_with_saved_declarations = set()
        if not os.path.exists(self.savepoint_file_path):
            open(self.savepoint_file_path, 'w').close()
        with open(self.savepoint_file_path, 'r') as file:
            for line in file:
                self.peps_with_saved_declarations.add(int(line))
        self.savepoint_file = open(self.savepoint_file_path, 'a')
        self.converter = DeclarationConverter()

    def add_arguments(self, parser):
        parser.add_argument('--pep_source_id', nargs='?', type=int)
        parser.add_argument('--pep_id', nargs='?', type=int)

    def add_pep_to_savepoint(self, nacp_declarant_id):
        if not self.is_pep_saved(nacp_declarant_id):
            self.savepoint_file.write(f'{nacp_declarant_id}\n')
            self.peps_with_saved_declarations.add(int(nacp_declarant_id))

    def is_pep_saved(self, nacp_declarant_id):
        return int(nacp_declarant_id) in self.peps_with_saved_declarations

    def load_one(self, pep: Pep):
        for nacp_id in pep.nacp_id:
            if not self.is_pep_saved(nacp_id):
                self.converter.save_declarations_for_pep(nacp_declarant_id=nacp_id)
                self.add_pep_to_savepoint(nacp_id)

    def load_all(self):
        i = 0
        for nacp_declarant_id in self.converter.only_peps:
            i += 1
            self.stdout.write(f'\rStart process for pep #{i}', ending='')
            self.stdout.flush()
            if not self.is_pep_saved(nacp_declarant_id):
                self.converter.save_declarations_for_pep(nacp_declarant_id=nacp_declarant_id)
                self.add_pep_to_savepoint(nacp_declarant_id)
        self.stdout.write()

    def handle(self, *args, **options):
        pep_source_id = options['pep_source_id']
        pep_id = options['pep_id']

        if pep_source_id:
            self.load_one(Pep.objects.get(source_id=pep_source_id))
        elif pep_id:
            self.load_one(Pep.objects.get(id=pep_id))
        else:
            self.load_all()
        self.stdout.write('Done!')
