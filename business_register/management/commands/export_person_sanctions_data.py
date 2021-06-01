from business_register.management.commands._base_export_command import BaseExportCommand
from business_register.models.sanction_models import PersonSanction
from business_register.serializers.sanction_serializers import (
    PersonSanctionSerializer
)


class Command(BaseExportCommand):
    help = 'Saves ALL PEPs data to file in "export/" directory'

    queryset = PersonSanction.objects.all()
    prefetch_related = ['types_of_sanctions', 'countries_of_citizenship']
    serializer_class = PersonSanctionSerializer
    file_code_name = 'person_sanction'
