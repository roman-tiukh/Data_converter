from business_register.management.commands._base_export_command import BaseExportCommand
from business_register.models.sanction_models import CompanySanction
from business_register.serializers.sanction_serializers import (
    CompanySanctionSerializer
)


class Command(BaseExportCommand):
    help = 'Saves ALL PEPs data to file in "export/" directory'

    queryset = CompanySanction.objects.all()
    select_related = ['country_of_registration']
    prefetch_related = ['types_of_sanctions']
    serializer_class = CompanySanctionSerializer
    file_code_name = 'company_sanction'
