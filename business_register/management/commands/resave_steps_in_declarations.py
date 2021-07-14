from django.core.management.base import BaseCommand
from business_register.converter.declaration import DeclarationConverter
from data_ocean.savepoint import Savepoint
from business_register.models.declaration_models import Declaration, Transaction, Liability, Property


class Command(BaseCommand):
    help = 'Saves Companies data into DB'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.converter = DeclarationConverter()
        self.savepoint = Savepoint('declarations_steps', type=str)

    def add_arguments(self, parser):
        pass

    def resave_transactions(self, data, declaration):
        Transaction.objects.filter(declaration=declaration).delete()
        self.converter.save_transaction(data, declaration)

    def resave_liability(self, data, declaration):
        Liability.objects.filter(declaration=declaration).delete()
        self.converter.save_liability(data, declaration)

    def resave_property(self, data, declaration):
        Property.objects.filter(declaration=declaration).exclude(
            type=Property.UNFINISHED_CONSTRUCTION,
        ).delete()
        self.converter.save_property(data, declaration)

    def resave_unfinished_construction(self, data, declaration):
        Property.objects.filter(
            declaration=declaration, type=Property.UNFINISHED_CONSTRUCTION,
        ).delete()
        self.converter.save_unfinished_construction(data, declaration)

    def resave_all_steps_with_city(self, data, declaration):
        self.converter.save_declarant_data(data, declaration)
        self.resave_liability(data, declaration)
        self.resave_property(data, declaration)
        self.resave_unfinished_construction(data, declaration)

    def process_declaration(self, data, declaration):
        # self.resave_transactions(data, declaration)
        self.resave_all_steps_with_city(data, declaration)

    def handle(self, *args, **options):
        i = 0
        qs = Declaration.objects.all()
        count = qs.count()
        for declaration in qs:
            i += 1
            self.stdout.write(f'\rProgress: {i} of {count}', ending='')
            self.stdout.flush()
            if self.savepoint.has(declaration.nacp_declaration_id):
                continue
            self.converter.current_declaration = declaration
            data = self.converter.download_declaration(str(declaration.nacp_declaration_id))
            if not data:
                raise Exception(f'No data for declaration {declaration.nacp_declaration_id}')
            self.converter.save_relatives_data(data, declaration)
            self.process_declaration(
                data=data,
                declaration=declaration
            )
            self.savepoint.add(declaration.nacp_declaration_id)
        self.savepoint.close()
        self.stdout.write()
        self.stdout.write('Done!')
