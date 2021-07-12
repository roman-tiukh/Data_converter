from django.core.management.base import BaseCommand
from business_register.converter.declaration import DeclarationConverter
from data_ocean.savepoint import Savepoint
from business_register.models.declaration_models import Declaration, Transaction


class Command(BaseCommand):
    help = 'Saves Companies data into DB'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.converter = DeclarationConverter()
        self.savepoint = Savepoint('declarations_transactions', type=str)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for declaration in Declaration.objects.all():
            if self.savepoint.has(declaration.nacp_declaration_id):
                continue
            self.converter.current_declaration = declaration
            data = self.converter.download_declaration(str(declaration.nacp_declaration_id))
            if not data:
                raise Exception(f'No data for declaration {declaration.nacp_declaration_id}')
            self.converter.save_relatives_data(data, declaration)
            Transaction.objects.filter(declaration=declaration).delete()
            self.converter.save_transaction(data, declaration)
            self.savepoint.add(declaration.nacp_declaration_id)
        self.savepoint.close()
