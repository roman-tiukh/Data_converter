from django.core.management.base import BaseCommand
from business_register.models.declaration_models import Declaration


class Command(BaseCommand):
    help = '---'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--rules', type=str, nargs='?', help='Example: PEP01,PEP03,PEP15')
        parser.add_argument('-a', '--all', dest='all', action='store_true')
        parser.add_argument('year', type=int, nargs=1)

    def handle(self, *args, **options):
        year = options['year'][0]
        rules = options['rules']
        calculate_all_declarations = options['all']
        if rules:
            rules = [rule.strip() for rule in rules.split(',')]
        else:
            rules = None
        qs = Declaration.objects.filter(year=year)
        if not calculate_all_declarations:
            qs = qs.filter(type=Declaration.ANNUAL)
        count = qs.count()
        i = 0
        for declaration in qs:
            i += 1
            self.stdout.write(f'\r Process {i} of {count}', ending='')
            self.stdout.flush()
            declaration.recalculate_scoring(rules)

        self.stdout.write()
        self.stdout.write('>>> Done!')
