from business_register.management.commands._base_export_command import BaseExportCommand
from business_register.models.pep_models import Pep
from business_register.serializers.company_and_pep_serializers import (
    PepDetailWithoutCheckCompaniesSerializer
)


class Command(BaseExportCommand):
    help = 'Saves ALL PEPs data to file in "export/" directory'

    queryset = Pep.objects.all()
    prefetch_related = [
        'from_person_links', 'to_person_links',
        'to_person_links__from_person', 'from_person_links__to_person',
    ]
    serializer_class = PepDetailWithoutCheckCompaniesSerializer
    file_code_name = 'pep'
