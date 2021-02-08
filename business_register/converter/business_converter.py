import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from business_register.models.kved_models import Kved
from business_register.models.company_models import Company
from data_ocean.converter import Converter
from data_ocean.models import Authority, Status, TaxpayerType


def find_company_by_edrpou(edprou):
    if edprou == '00000000':
        return None
    queryset = Company.objects.filter(edrpou=edprou)
    if len(queryset) == 1:
        return queryset[0]
    if not len(queryset):
        return None
    return queryset.order_by('status').first()


class BusinessConverter(Converter):
    """
    here we have common functions for Fop and Company converters
    """

    def __init__(self):
        """
        declaring as class fields for global access and initializing dictionaries with all kveds, /
        statuses, authorities and taxpayer_types from DB
        """
        self.all_kveds_dict = self.put_all_kveds_to_dict()
        self.all_statuses_dict = self.put_objects_to_dict("name", "data_ocean", "Status")
        self.all_authorities_dict = self.put_objects_to_dict("name", "data_ocean", "Authority")
        self.all_taxpayer_types_dict = self.put_objects_to_dict("name", "data_ocean", "TaxpayerType")
        super().__init__()

    def find_edrpou(self, string_to_check):
        return len(string_to_check) == 8 and string_to_check.isdigit()

    def put_all_kveds_to_dict(self):
        return {kved.code+kved.name: kved for kved in Kved.objects.all()}

    def get_kved_from_DB(self, kved_code_from_record, kved_name_from_record):
        """
        retreiving kved from DB
        """
        kved_key = kved_code_from_record + kved_name_from_record.lower()
        if kved_key in self.all_kveds_dict:
            return self.all_kveds_dict[kved_key]
        logger.info('Kved name is not valid: ' + kved_name_from_record)
        return self.all_kveds_dict['not_validnot_valid']

    def save_or_get_status(self, status_from_record):
        """
        retreiving status from DB or storing the new one
        """
        status = status_from_record.lower()
        if status not in self.all_statuses_dict:
            new_status = Status.objects.create(name=status)
            self.all_statuses_dict[status] = new_status
            return new_status
        return self.all_statuses_dict[status]

    def save_or_get_authority(self, authority_from_record):
        """
        retreiving authority from DB or storing the new one
        """
        authority = authority_from_record.lower()
        if authority not in self.all_authorities_dict:
            new_authority = Authority.objects.create(name=authority)
            self.all_authorities_dict[authority] = new_authority
            return new_authority
        return self.all_authorities_dict[authority]

    def save_or_get_taxpayer_type(self, taxpayer_type_from_record):
        """
        retreiving taxpayer_type from DB or storing the new one
        """
        taxpayer_type = taxpayer_type_from_record.lower()
        if taxpayer_type not in self.all_taxpayer_types_dict:
            new_taxpayer_type = TaxpayerType.objects.create(name=taxpayer_type)
            self.all_taxpayer_types_dict[taxpayer_type] = new_taxpayer_type
            return new_taxpayer_type
        return self.all_taxpayer_types_dict[taxpayer_type]

    def extract_kved(self, kved_data):
        kved_info = kved_data.split(' ', 1)
        kved_code = kved_info[0]
        kved_name = kved_info[1]
        return self.get_kved_from_DB(kved_code, kved_name)
