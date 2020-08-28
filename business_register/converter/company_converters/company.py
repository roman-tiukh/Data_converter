from business_register.converter.business_converter import BusinessConverter
from business_register.models.company_models import CompanyType


class CompanyConverter(BusinessConverter):
    def __init__(self):
        self.all_company_type_dict = self.put_all_objects_to_dict('name', "business_register",
                                                                  "CompanyType")
        super().__init__()

    def save_or_get_company_type(self, type_from_record):
        company_type = type_from_record.lower()
        if company_type not in self.all_company_type_dict:
            company_type = CompanyType.objects.create(name=company_type)
            self.all_company_type_dict[company_type] = company_type
            return company_type
        else:
            return self.all_company_type_dict[company_type]
