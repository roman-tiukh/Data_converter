from django.core.management import BaseCommand
from business_register.converter.declaration import DeclarationConverter


class Command(BaseCommand):
    help = '---'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        converter = DeclarationConverter()
        i = 0
        for nacp_declarant_id in converter.only_peps:
            i += 1
            self.stdout.write(f'\rStart process for pep #{i}', ending='')
            self.stdout.flush()
            converter.save_declarations_for_pep(nacp_declarant_id=nacp_declarant_id)
        self.stdout.write()
        self.stdout.write('Done!')
