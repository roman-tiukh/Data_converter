import re

from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from business_register.models.sanction_models import CompanySanction, SanctionType
from data_ocean.utils import replace_incorrect_symbols
from location_register.models.address_models import Country


class Command(BaseCommand):
    help = 'Load companies sanctions'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start-row', type=int, nargs='?', default=1)

    def handle(self, *args, **options):
        start_row = options['start_row']
        wb = load_workbook('./source_data/data_for_upload/normalized_companies_210521.xlsx')
        reasoning = (
            'рішення Ради національної безпеки і оборони України '
            'від 14 травня 2021 року "Про застосування персональних '
            'спеціальних економічних та інших обмежувальних заходів (санкцій)"'
        )
        ws = wb['Sheet']
        for i, row in enumerate(ws):
            if i < start_row:
                continue
            self.stdout.write(f'\r    Process row #{i}', ending='')
            row = [cell.value for cell in row]

            country_name = row[5]
            try:
                country = Country.objects.get(name=country_name)
            except Country.DoesNotExist:
                self.stdout.write(f'\n    Країну не знайдено: "{country_name}"')
                exit(1)

            company = CompanySanction.objects.create(
                address=row[2] or '',
                name=row[3],
                name_original=row[4] or '',
                country_of_registration=country,

                registration_number=row[6] or '',
                taxpayer_number=row[7] or '',
                # additional_info=row[8] or '',

                end_date=row[9],
                start_date=row[10],

                # registration_date=row[12],

                reasoning=reasoning,
            )

            for sanction_type_name in row[8].split('&&'):
                sanction_type_name = replace_incorrect_symbols(sanction_type_name.strip())
                sanction_type, created = SanctionType.objects.get_or_create(
                    name=sanction_type_name,
                    defaults={'law': 'про санкції'},
                )
                if created:
                    self.stdout.write(f'\n    Створено новий тип санкції: {sanction_type_name}')
                company.types_of_sanctions.add(sanction_type)

            company.save()
        self.stdout.write('\n    Done!')
