from django.core.management import BaseCommand
from business_register.converter.declaration import DeclarationConverter
from business_register.models.pep_models import Pep


class Command(BaseCommand):
    help = '---'

    def add_arguments(self, parser):
        parser.add_argument('--pep_source_id', nargs='?', type=int)
        parser.add_argument('--pep_id', nargs='?', type=int)

    def load_one(self, pep: Pep):
        for nacp_id in pep.nacp_id:
            self.converter.save_declarations_for_pep(nacp_declarant_id=nacp_id)

    def load_all(self):
        i = 0
        for nacp_declarant_id in self.converter.only_peps:
            i += 1
            self.stdout.write(f'\rStart process for pep #{i}', ending='')
            self.stdout.flush()
            self.converter.save_declarations_for_pep(nacp_declarant_id=nacp_declarant_id)
        self.stdout.write()

    def handle(self, *args, **options):
        self.converter = DeclarationConverter()
        pep_source_id = options['pep_source_id']
        pep_id = options['pep_id']

        if pep_source_id:
            self.load_one(Pep.objects.get(source_id=pep_source_id))
        elif pep_id:
            self.load_one(Pep.objects.get(id=pep_id))
        else:
            self.load_all()
        self.stdout.write('Done!')
