from django.core.management.base import BaseCommand
from business_register.models.company_models import CompanyType
from business_register.converter.company_converters.company import CompanyConverter


class Command(BaseCommand):
    help = 'Translate all company types names'

    def handle(self, *args, **options):
        for company_type in CompanyType.objects.all():
            update_fields = []
            if company_type.name and not company_type.name_eng:
                company_type.name_eng = CompanyConverter().COMPANY_TYPES_UK_EN.get(company_type.name)
                update_fields.append('name_eng')
            if not company_type.name and company_type.name_eng:
                for key, value in CompanyConverter().COMPANY_TYPES_UK_EN.items():
                    if value == company_type.name_eng:
                        company_type.name = key
                        update_fields.append('name')
                        break
            if update_fields:
                update_fields.append('updated_at')
                company_type.save(update_fields=update_fields)
