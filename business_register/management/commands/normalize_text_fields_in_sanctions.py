from django.core.management.base import BaseCommand
from django.db import IntegrityError

from business_register.models.sanction_models import CompanySanction, PersonSanction, SanctionType
import re

general_field = (
    'cancellation_condition',
    'reasoning',
)

company_fields = (
    'name',
    'name_original_transcription',
    'address',
    'registration_number',
    'taxpayer_number',
    'additional_info',
)

person_fields = (
    'first_name',
    'middle_name',
    'last_name',
    'full_name',
    'full_name_original_transcription',
    'place_of_birth',
    'address',
    'occupation',
    'id_card',
    'taxpayer_number',
    'additional_info',
)

sanction_type_fields = (
    'name',
)


class Command(BaseCommand):
    help = 'Normalize strings in models'

    def add_arguments(self, parser):
        pass

    @staticmethod
    def remove_symbols(string):
        string = string \
            .replace('\t', ' ') \
            .replace('\r', '') \
            .replace('\n', ' ') \
            .replace('’', "'") \
            .replace('—', '-') \
            .replace('–', '-') \
            .replace('−', '-') \
            .replace('\xa0', ' ') \
            .replace('«', '"') \
            .replace('»', '"') \
            .replace("''", '"')
        string = re.sub(r'\s+', ' ', string)
        return string

    def normalize(self, obj, field) -> bool:
        value = getattr(obj, field)
        if not value:
            return False

        new_value = self.remove_symbols(value)
        if value != new_value:
            setattr(obj, field, self.remove_symbols(value))
            return True
        return False

    def process_model(self, model, fields):
        self.stdout.write(f'Start process for model {model}')
        i = 0
        for obj in model.objects.all():
            need_to_save = False
            for field in fields:
                is_changed = self.normalize(obj, field)
                if is_changed:
                    need_to_save = True
            if need_to_save:
                try:
                    obj.save()
                except IntegrityError:
                    self.stdout.write(f'\nIntegrityError at model {model} object_id - {obj.pk}')
            i += 1
            self.stdout.write(f'\rProcessed {i}', ending='')
        self.stdout.write()
        self.stdout.write(f'Finish process for model {model}')

    def handle(self, *args, **options):
        self.process_model(CompanySanction, general_field + company_fields)
        self.process_model(PersonSanction, general_field + person_fields)
        self.process_model(SanctionType, sanction_type_fields)
        self.stdout.write('Done!')
