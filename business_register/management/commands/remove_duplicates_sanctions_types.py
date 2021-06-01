from django.core.management.base import BaseCommand
from business_register.models.sanction_models import SanctionType


class Command(BaseCommand):
    help = 'Removes duplicates of types of sanctions'

    def add_arguments(self, parser):
        parser.add_argument('ids', type=int, nargs='+')

    def handle(self, *args, **options):
        ids = options['ids']
        if len(ids) < 2:
            raise ValueError('2 ids min')
        main = ids[0]
        duplicates = set(ids[1:])
        main_st: SanctionType = SanctionType.objects.get(id=main)
        duplicates_st: [SanctionType] = SanctionType.objects.filter(id__in=duplicates)

        moved_persons, moved_companies, moved_countries = main_st.relink_duplicates(duplicates_st)
        deleted_sanction_types = SanctionType.clean_empty()

        self.stdout.write(f'Moved person sanctions - {moved_persons}')
        self.stdout.write(f'Moved company sanctions - {moved_companies}')
        self.stdout.write(f'Moved country sanctions - {moved_countries}')
        self.stdout.write(f'Deleted sanction types - {deleted_sanction_types}')
