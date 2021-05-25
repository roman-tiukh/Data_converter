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

        moved_cs = 0
        moved_ps = 0

        for st in duplicates_st:
            for cs in list(st.companies_under_sanction.all()):
                cs.types_of_sanctions.remove(st)
                cs.types_of_sanctions.add(main_st)
                moved_cs += 1
                self.stdout.write(f'\rMoved CS - {moved_cs}; Moved PS - {moved_ps}')
            for ps in list(st.persons_under_sanction.all()):
                ps.types_of_sanctions.remove(st)
                ps.types_of_sanctions.add(main_st)
                moved_ps += 1
                self.stdout.write(f'\rMoved CS - {moved_cs}; Moved PS - {moved_ps}')
            for country_sanction in list(st.countries_under_sanction.all()):
                country_sanction.types_of_sanctions.remove(st)
                country_sanction.types_of_sanctions.add(main_st)
                self.stdout.write(f'\rMoved CS - {moved_cs}; Moved PS - {moved_ps}')
        self.stdout.write()
