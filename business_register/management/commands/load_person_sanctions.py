from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from business_register.models.sanction_models import PersonSanction, SanctionType
from location_register.models.address_models import Country


class Command(BaseCommand):
    help = 'Load person sanctions'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start-row', type=int, nargs='?', default=1)

    def handle(self, *args, **options):
        start_row = options['start_row']
        wb = load_workbook('./source_data/data_for_upload/normalized_dodatok1.xlsx')
        reasoning = (
            'рішення Ради національної безпеки і оборони України від 21 червня 2018 року '
            '"Про застосування та внесення змін до персональних спеціальних економічних '
            'та інших обмежувальних заходів (санкцій)"'
        )
        ws = wb['Sheet']
        for i, row in enumerate(ws):
            if i < start_row:
                continue
            self.stdout.write(f'\r    Process row #{i}', ending='')
            row = [cell.value for cell in row]

            countries = []
            for country in row[5].split('&&'):
                country = country.strip().lower()
                try:
                    countries.append(Country.objects.get(name=country))
                except Country.DoesNotExist:
                    self.stdout.write(f'\n    Країну не знайдено: {country}')
                    exit(1)

            person = PersonSanction.objects.create(
                first_name=row[2],
                last_name=row[3],
                middle_name=row[4] or '',
                full_name=f'{row[3]} {row[2]} {row[4]}',
                full_name_original_transcription=row[6] or '',
                date_of_birth=row[7],
                end_date=row[9],
                start_date=row[11],
                place_of_birth=row[12] or '',
                address=row[13] or '',
                occupation=row[14] or '',
                taxpayer_number=row[15] or '',
                id_card=row[16] or '',
                additional_info=row[17] or '',

                reasoning=reasoning,
            )

            for country in countries:
                person.countries_of_citizenship.add(country)

            for sanction_type_name in row[8].split('&&'):
                sanction_type_name = sanction_type_name.strip()
                sanction_type, created = SanctionType.objects.get_or_create(
                    name=sanction_type_name,
                    defaults={'law': 'про санкції'},
                )
                if created:
                    self.stdout.write(f'\n    Створено новий тип санкції: {sanction_type_name}')
                person.types_of_sanctions.add(sanction_type)

            person.save()
        self.stdout.write('\n    Done')

