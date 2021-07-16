from django.core.management.base import BaseCommand, CommandError
from business_register.models.declaration_models import Declaration, PepScoring
from business_register.pep_scoring.rules_registry import ALL_RULES, ScoringRuleEnum


class Command(BaseCommand):
    help = '---'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--all', dest='all', action='store_true')
        parser.add_argument('--year', type=int, nargs='?')
        parser.add_argument('--declaration_id', nargs='?', type=str)
        parser.add_argument(
            '-r', '--rule', dest='rules', type=str, action='append',
            choices=[rule.value for rule in ScoringRuleEnum]
        )

    def handle(self, *args, **options):
        year = options['year']
        rules = options['rules']
        declaration_id = options['declaration_id']
        calculate_all_declarations = options['all']

        params = (year, declaration_id)
        if not any(params) or all(params):
            raise CommandError('Pass --year or --declaration_id for this command')

        if year:
            qs = Declaration.objects.filter(year=year)
            if not calculate_all_declarations:
                qs = qs.filter(type=Declaration.ANNUAL)
        else:
            qs = Declaration.objects.filter(nacp_declaration_id=declaration_id)

        count = qs.count()
        i = 0
        for declaration in qs:
            i += 1
            self.stdout.write(f'\r Process {i} of {count}', ending='')
            self.stdout.flush()
            declaration.recalculate_scoring(rules)

        PepScoring.refresh_coefficient()
        self.stdout.write()
        self.stdout.write('Done. Scoring coefficient refreshed.')
