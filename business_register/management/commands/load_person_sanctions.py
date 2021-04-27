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
        wb = load_workbook('./source_data/data_for_upload/normalized_pers_sanc_28_04_2017.xlsx')
        reasoning = (
            'рішення Ради національної безпеки і оборони України від 28 квітня 2017 року '
            '"Про застосування персональних спеціальних економічних та '
            'інших обмежувальних заходів (санкцій)'
        )
        ws = wb['Sheet']
        for i, row in enumerate(ws):
            if i < start_row:
                continue
            self.stdout.write(f'\r Process row #{i}', ending='')
            row = [cell.value for cell in row]
            person = PersonSanction.objects.create(
                first_name=row[2],
                last_name=row[3],
                middle_name=row[4] or '',
                full_name=f'{row[3]} {row[2]} {row[4]}',
                place_of_birth=row[6] or '',
                id_card=row[8] or '',
                taxpayer_number=row[9] or '',
                address=row[10] or '',
                occupation=row[11] or '',
                full_name_original_transcription=row[12] or '',
                date_of_birth=row[13],
                end_date=row[15],
                start_date=row[17],
                reasoning=reasoning,
            )

            for country in row[5].split('&&'):
                country = country.strip().lower()
                try:
                    person.countries_of_citizenship.add(Country.objects.get(name=country))
                except Country.DoesNotExist:
                    self.stdout.write(f'\n Країну не знайдено: {country}')
                    exit(1)

            for sanction_type_name in row[14].split('&&'):
                sanction_type_name = sanction_type_name.strip()
                sanction_type, created = SanctionType.objects.get_or_create(
                    name=sanction_type_name,
                    defaults={'law': 'про санкції'},
                )
                if created:
                    self.stdout.write(f'\n Створено новий тип санкції: {sanction_type_name}')
                person.types_of_sanctions.add(sanction_type)

            person.save()
        self.stdout.write('\n Done')
