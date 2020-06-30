from django.apps import apps

from business_register.models.kved_models import Kved
from data_ocean.models import Authority, Status, TaxpayerType
from data_ocean.converter import Converter


class BusinessConverter(Converter):
    """
    here we have common functions for Fop and Company converters
    """

    def __init__(self):
        """
        declaring as class fields for global access and initializing dictionaries with all kveds, /
        statuses, authorities and taxpayer_types from DB
        """
        self.all_kveds_dict = self.put_all_objects_to_dict("code", "business_register", "Kved")
        self.all_statuses_dict = self.put_all_objects_to_dict("name", "data_ocean", "Status")
        self.all_authorities_dict = self.put_all_objects_to_dict("name", "data_ocean", "Authority")
        self.all_taxpayer_types_dict = self.put_all_objects_to_dict("name", "data_ocean", "TaxpayerType")

    def put_all_objects_to_dict(self, key_field, app_name, model_name):
        return {getattr(obj, key_field): obj
                for obj in apps.get_model(app_name, model_name).objects.all()}

    def get_kved_from_DB(self, kved_code_from_record):
        """
        retreiving kved from DB
        """
        if kved_code_from_record in self.all_kveds_dict:
            return self.all_kveds_dict[kved_code_from_record]
        return Kved.objects.get(code='EMP')

    def save_or_get_status(self, status_from_record):
        """
        retreiving status from DB or storing the new one
        """
        if status_from_record not in self.all_statuses_dict:
            new_status = Status.objects.create(name=status_from_record)
            self.all_statuses_dict[status_from_record] = new_status
            return new_status
        return self.all_statuses_dict[status_from_record]

    def save_or_get_authority(self, authority_from_record):
        """
        retreiving authority from DB or storing the new one
        """
        if authority_from_record not in self.all_authorities_dict:
            new_authority = Authority.objects.create(name=authority_from_record)
            self.all_authorities_dict[authority_from_record] = new_authority
            return new_authority
        return self.all_authorities_dict[authority_from_record]

    def save_or_get_taxpayer_type(self, taxpayer_type_from_record):
        """
        retreiving taxpayer_type from DB or storing the new one
        """
        if taxpayer_type_from_record not in self.all_taxpayer_types_dict:
            new_taxpayer_type = TaxpayerType.objects.create(name=taxpayer_type_from_record)
            self.all_taxpayer_types_dict[taxpayer_type_from_record] = new_taxpayer_type
            return new_taxpayer_type
        return self.all_taxpayer_types_dict[taxpayer_type_from_record]
