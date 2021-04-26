from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from business_register.models.sanction_models import PersonSanction, SanctionType
from location_register.models.address_models import Country


class Command(BaseCommand):
    help = 'Load person sanctions'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        wb = load_workbook('./source_data/data_for_upload/normalized_pers_sanc_14_05 _FULL (copy).xlsx')
        reasoning = (
            'рішення Ради національної безпеки і оборони України від 14 травня 2020 року '
            '"Про застосування, скасування і внесення змін до персональних спеціальних економічних '
            'та інших обмежувальних заходів (санкцій)'
        )
        ws = wb['Sheet']
        for i, row in enumerate(ws):
            self.stdout.write(f'Process row #{i + 1}', ending='\r')
            if i == 0:
                continue
            row = [cell.value for cell in row]
            person = PersonSanction.objects.create(
                first_name=row[2],
                last_name=row[3],
                middle_name=row[4] or '',
                full_name=f'{row[3]} {row[2]} {row[4]}',
                full_name_original_transcription=row[6] or '',
                date_of_birth=row[7],
                reasoning=reasoning,
                end_date=row[9],
                start_date=row[11],
                place_of_birth=row[12] or '',
                address=row[13] or '',
                id_card=row[14] or '',
            )

            for country in row[5].split('&&'):
                country = country.strip().lower()
                person.countries_of_citizenship.add(Country.objects.get(name=country))

            for sanction_type_name in row[8].split('&&'):
                sanction_type_name = sanction_type_name.strip()
                sanction_type, created = SanctionType.objects.get_or_create(
                    name=sanction_type_name,
                    defaults={'law': 'про санкції'},
                )
                person.types_of_sanctions.add(sanction_type)

            person.save()
