import re
from datetime import date

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
        wb = load_workbook('./source_data/data_for_upload/u266_id4920_dod2_norm.xlsx')
        reasoning = (
            'рішення Ради національної безпеки і оборони України від 18 червня 2021 року '
            '"Про застосування персональних спеціальних економічних та інших обмежувальних заходів (санкцій)"'
        )
        reasoning_date = date(2021, 6, 18)

        ws = wb['Sheet']
        for i, row in enumerate(ws):
            if i < start_row:
                continue
            self.stdout.write(f'\r    Process row #{i}', ending='')
            row = [cell.value for cell in row]

            country_name = row[4]
            try:
                country = Country.objects.get(name=country_name)
            except Country.DoesNotExist:
                self.stdout.write(f'\n    Країну не знайдено: "{country_name}"')
                exit(1)

            company = CompanySanction.objects.create(
                initial_data=row[1],
                name=row[2],
                name_original=row[3] or '',
                registration_number=row[5] or '',
                taxpayer_number=row[6] or '',
                country_of_registration=country,
                end_date=row[8],
                start_date=row[9],
                registration_date=row[10],
                address=row[11] or '',
                additional_info=row[12] or '',
                reasoning=reasoning,
                reasoning_date=reasoning_date,
            )

            for sanction_type_name in row[7].split('&&'):
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
