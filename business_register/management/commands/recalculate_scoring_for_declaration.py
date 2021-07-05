from django.core.management.base import BaseCommand
from business_register.models.declaration_models import Declaration
from business_register.pep_scoring.constants import ScoringRuleEnum
from business_register.pep_scoring.rules import ALL_RULES, BaseScoringRule


class Command(BaseCommand):
    help = '---'

    def add_arguments(self, parser):
        parser.add_argument('declaration_id', type=str, nargs=1)

    def handle(self, *args, **options):
        declaration_id = options['declaration_id'][0]
        if declaration_id.isdigit():
            declaration_id = int(declaration_id)
            declaration = Declaration.objects.get(id=declaration_id)
        else:
            declaration = Declaration.objects.get(nacp_declaration_id=declaration_id)
        declaration.recalculate_scoring()
