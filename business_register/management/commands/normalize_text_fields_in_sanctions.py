from django.core.management.base import BaseCommand
from business_register.models.sanction_models import CompanySanction, PersonSanction, SanctionType
from data_ocean.utils import replace_incorrect_symbols


general_field = (
    'initial_data',
    'cancellation_condition',
    'reasoning',
)

company_fields = (
    'name',
    'name_original',
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
    'full_name_original',
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
    def normalize(obj, field) -> bool:
        value = getattr(obj, field)
        if not value:
            return False

        new_value = replace_incorrect_symbols(value)
        if value != new_value:
            setattr(obj, field, new_value)
            return True
        return False

    def normalize_sanction_type(self, obj, field) -> bool:
        value = getattr(obj, field)
        if not value:
            return False

        new_value = replace_incorrect_symbols(value)
        if value != new_value:
            st: SanctionType = SanctionType.objects.filter(name=new_value).order_by('id').first()
            if st:
                self.stdout.write(f'\nDuplicate detected - SanctionType - {st.pk} and {obj.pk}')
                persons, companies, countries = st.relink_duplicates([obj])
                self.stdout.write(f'Moved: persons - {persons}, companies - {companies}, countries - {countries}')
            else:
                setattr(obj, field, new_value)
                return True
        return False

    def process_model(self, model, fields, normalize_method):
        self.stdout.write(f'Start process for model {model}')
        i = 0
        for obj in model.objects.all():
            need_to_save = False
            for field in fields:
                is_changed = normalize_method(obj, field)
                if is_changed:
                    need_to_save = True
            if need_to_save:
                obj.save()
            i += 1
            self.stdout.write(f'\rProcessed {i}', ending='')
        self.stdout.write()
        self.stdout.write(f'Finish process for model {model}')

    def handle(self, *args, **options):
        self.process_model(CompanySanction, general_field + company_fields, self.normalize)
        self.process_model(PersonSanction, general_field + person_fields, self.normalize)
        self.process_model(SanctionType, sanction_type_fields, self.normalize_sanction_type)
        deleted_st = SanctionType.clean_empty()
        self.stdout.write(f'Deleted SanctionType - {deleted_st}')
        self.stdout.write('Done!')
