import re
from datetime import date

from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from business_register.models.sanction_models import PersonSanction, SanctionType
from data_ocean.utils import replace_incorrect_symbols
from location_register.models.address_models import Country


class Command(BaseCommand):
    help = 'Load person sanctions'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start-row', type=int, nargs='?', default=1)

    def handle(self, *args, **options):
        start_row = options['start_row']
        wb = load_workbook('./source_data/data_for_upload/u266_id4920_dod1_norm.xlsx')
        reasoning = (
            'рішення Ради національної безпеки і оборони України від 18 червня 2021 року '
            '"Про застосування персональних спеціальних економічних та інших обмежувальних заходів (санкцій)"'
        )
        reasoning_date = date(2021, 6, 18)
        ws = wb['Sheet']
        for i, row in enumerate(ws):
            if i < start_row:
                continue
            # print(row[1].value)
            # exit()
            self.stdout.write(f'\r    Process row #{i}', ending='')
            row = [cell.value for cell in row]

            countries_fu = []
            countries = row[5]
            if '&&' in countries:
                countries = countries.split('&&')
            else:
                countries = countries.split(',')
            countries = [x.strip() for x in countries]
            for country in countries:
                country = country.strip().lower()
                try:
                    countries_fu.append(Country.objects.get(name=country))
                except Country.DoesNotExist:
                    self.stdout.write(f'\n    Країну не знайдено: {country}')
                    exit(1)

            person = PersonSanction.objects.create(
                initial_data=row[1],
                first_name=row[2],
                last_name=row[3],
                middle_name=row[4] or '',
                full_name=f'{row[3]} {row[2]} {row[4] or ""}',
                full_name_original=row[6] or '',
                end_date=row[9],
                start_date=row[10],
                place_of_birth=row[11] or '',
                address=row[12] or '',
                occupation=row[13] or '',
                id_card=row[14] or '',
                passports=[x.strip() for x in str(row[15]).split(',')] if row[15] else [],
                additional_info=row[16] or '',
                taxpayer_number=row[17] or '',

                reasoning=reasoning,
                reasoning_date=reasoning_date,
            )
            date_of_birth = row[7]
            year_of_birth = row[18]
            if date_of_birth:
                if type(date_of_birth) == int:
                    person.year_of_birth = date_of_birth
                else:
                    person.date_of_birth = date_of_birth
            if year_of_birth:
                person.year_of_birth = year_of_birth

            for country in countries_fu:
                person.countries_of_citizenship.add(country)

            for sanction_type_name in row[8].split('&&'):
                sanction_type_name = replace_incorrect_symbols(sanction_type_name.strip())
                sanction_type, created = SanctionType.objects.get_or_create(
                    name=sanction_type_name,
                    defaults={'law': 'про санкції'},
                )
                if created:
                    self.stdout.write(f'\n    Створено новий тип санкції: {sanction_type_name}')
                person.types_of_sanctions.add(sanction_type)

            person.save()
        self.stdout.write('\n    Done')

