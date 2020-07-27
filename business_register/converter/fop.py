import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from business_register.converter.business_converter import BusinessConverter
from business_register.models.fop_models import (ExchangeDataFop, Fop,
                                                 FopToKved)
from django.conf import settings
from data_ocean.converter import BulkCreateUpdateManager
from data_ocean.models import Register
from data_ocean.utils import get_first_word, cut_first_word, format_date_to_yymmdd


class FopConverter(BusinessConverter):

    def __init__(self):
        self.API_ADDRESS_FOR_DATASET = Register.objects.get(source_register_id=
                                                            "1c7f3815-3259-45e0-bdf1-64dca07ddc10").api_address
        self.LOCAL_FOLDER = settings.LOCAL_FOLDER
        self.LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_FOP
        self.CHUNK_SIZE = settings.CHUNK_SIZE_FOP
        self.RECORD_TAG = 'SUBJECT'
        self.bulk_manager = BulkCreateUpdateManager(1000000)
        self.all_fop_kveds = []
        self.all_fop_exchange_data = []
        self.all_fops_dict = self.put_all_objects_to_dict('code', 'business_register', 'Fop')
        super().__init__()

    def update_fop_fields(self, code, status, registration_date, registration_info,
                          estate_manager, termination_date, terminated_info,
                          termination_cancel_info, contact_info, vp_dates, authority):
        fop = self.all_fops_dict[code]
        fop.status = status
        fop.registration_date = registration_date
        fop.registration_info = registration_info
        fop.estate_manager = estate_manager
        fop.termination_date = termination_date
        fop.terminated_info = terminated_info
        fop.termination_cancel_info = termination_cancel_info
        fop.contact_info = contact_info
        fop.vp_dates = vp_dates
        fop.authority = authority
        return fop

    def create_new_fop(self, code, fullname, address, status, registration_date,
                       registration_info, estate_manager, termination_date, terminated_info,
                       termination_cancel_info, contact_info, vp_dates, authority):
        fop = Fop(
            code=code,
            fullname=fullname,
            address=address,
            status=status,
            registration_date=registration_date,
            registration_info=registration_info,
            estate_manager=estate_manager,
            termination_date=termination_date,
            terminated_info=terminated_info,
            termination_cancel_info=termination_cancel_info,
            contact_info=contact_info,
            vp_dates=vp_dates,
            authority=authority)
        return fop

    # putting all kveds into a list
    def add_fop_kveds_to_list(self, fop_kveds, code):
        for activity in fop_kveds:
            info = activity.xpath('NAME')
            if not info:
                continue
            kved_name = info[0].text
            if kved_name:
                kved = self.get_kved_from_DB(kved_name)
            primary = activity.xpath('PRIMARY')[0].text == "так"
            self.all_fop_kveds.append({"code": code, "kved": kved, "primary": primary})

    # putting all exchange data into a list
    def add_exchange_data_to_list(self, exchange_data, code):
        for answer in exchange_data:
            info = answer.xpath('AUTHORITY_NAME')
            if not info:
                continue
            authority = self.save_or_get_authority(info[0].text)
            taxpayer_info = answer.xpath('TAX_PAYER_TYPE')
            taxpayer_type = None
            if taxpayer_info and taxpayer_info[0].text:
                taxpayer_type = self.save_or_get_taxpayer_type(taxpayer_info[0].text)
            start_date_info = answer.xpath('START_DATE')
            start_date = None
            if start_date_info and start_date_info[0].text:
                start_date = format_date_to_yymmdd(start_date_info[0].text)
            start_number_info = answer.xpath('START_NUM')
            start_number = None
            if start_number_info:
                start_number = start_number_info[0].text
            end_date_info = answer.xpath('END_DATE')
            end_date = None
            if end_date_info and end_date_info[0].text:
                end_date = format_date_to_yymmdd(end_date_info[0].text)
            end_number_info = answer.xpath('END_NUM')
            end_number = None
            if end_number_info:
                end_number = end_number_info[0].text
            self.all_fop_exchange_data.append({
                "code": code,
                "authority": authority,
                "taxpayer_type": taxpayer_type,
                "start_date": start_date,
                "start_number": start_number,
                "end_date": end_date,
                "end_number": end_number
            })

    def find_stored_fop(self, code):
        for fop in self.bulk_manager.update_queues['business_register.Fop']:
            if fop.code == code:
                return fop
        for fop in self.bulk_manager.create_queues['business_register.Fop']:
            if fop.code == code:
                return fop

    def add_fop_to_kved_to_bulk(self, fop, kved, primary_kved):
        fop_to_kved = FopToKved(fop=fop, kved=kved, primary_kved=primary_kved)
        self.bulk_manager.add_create(fop_to_kved)

    def save_fop_kveds_to_db(self):
        for dictionary in self.all_fop_kveds:
            fop = self.find_stored_fop(dictionary["code"])
            kved = dictionary["kved"]
            if kved.code == 'EMP':
                continue
            primary_kved = dictionary["primary"]
            stored = False
            # checking if the Fop`s kved is already in DB
            fop_to_kveds = FopToKved.objects.filter(fop=fop)
            if fop_to_kveds:
                for fop_to_kved in fop_to_kveds:
                    if fop_to_kved.kved == kved and fop_to_kved.primary_kved == primary_kved:
                        stored = True
                        break
            if not stored:
                # TODO: make an algorithm for kveds that the Fop doesn`t use anymore
                self.add_fop_to_kved_to_bulk(fop, kved, primary_kved)
        self.bulk_manager.commit_create(FopToKved)
        self.bulk_manager.create_queues['business_register.FopToKved'] = []
        self.all_fop_kveds = []

    def add_exchanged_data_fop_to_bulk(self, fop, authority, taxpayer_type, start_date,
                                       start_number, end_date, end_number):
        exchange_data = ExchangeDataFop(fop=fop, authority=authority, taxpayer_type=taxpayer_type,
                                        start_date=start_date, start_number=start_number,
                                        end_date=end_date, end_number=end_number)
        self.bulk_manager.add_create(exchange_data)

    def save_exchange_data_to_db(self):
        # variable for having the exchange_data from the same fop
        previous_fop = None
        for dictionary in self.all_fop_exchange_data:
            fop = self.find_stored_fop(dictionary["code"])
            authority = dictionary["authority"]
            taxpayer_type = dictionary["taxpayer_type"]
            start_date = dictionary["start_date"]
            start_number = dictionary["start_number"]
            end_date = dictionary["end_date"]
            end_number = dictionary["end_number"]
            stored = False
            if fop != previous_fop:
                fop_exchange_data = ExchangeDataFop.objects.filter(fop=fop)
            # checking if the Fop`s exchange_data is already in the the DB
            if fop_exchange_data:
                for exchange_data in fop_exchange_data:
                    if exchange_data.start_date:
                        exchange_data.start_date = str(exchange_data.start_date)
                    if exchange_data.end_date:
                        exchange_data.end_date = str(exchange_data.end_date)
                    if (exchange_data.authority == authority
                            and exchange_data.taxpayer_type == taxpayer_type
                            and exchange_data.start_date == start_date
                            and exchange_data.start_number == start_number
                            and exchange_data.end_date == end_date
                            and exchange_data.end_number == end_number):
                        stored = True
                        break
            if not stored:
                self.add_exchanged_data_fop_to_bulk(fop, authority, taxpayer_type, start_date,
                                                    start_number, end_date, end_number)
            previous_fop = fop
        if self.bulk_manager.create_queues['business_register.ExchangeDataFop']:
            self.bulk_manager.commit_create(ExchangeDataFop)
        self.bulk_manager.create_queues['business_register.ExchangeDataFop'] = []
        self.all_fop_exchange_data = []

    def save_to_db(self, records):
        for record in records:
            fullname = record.xpath('NAME')[0].text
            if not fullname:
                logger.warning(f'ФОП без прізвища: {record}')
                continue
            address = record.xpath('ADDRESS')[0].text
            if not address:
                address = 'EMPTY'
            code = fullname + address
            registration_text = record.xpath('REGISTRATION')[0].text
            termination_text = record.xpath('TERMINATED_INFO')[0].text
            status = self.save_or_get_status(record.xpath('STAN')[0].text)
            # first getting date, then registration info if REGISTRATION.text exists
            registration_date = None
            registration_info = None
            if registration_text:
                registration_date = format_date_to_yymmdd(get_first_word(registration_text))
                registration_info = cut_first_word(registration_text)
            estate_manager = record.xpath('ESTATE_MANAGER')[0].text
            termination_date = None
            terminated_info = None
            if termination_text:
                termination_date = format_date_to_yymmdd(get_first_word(termination_text))
                terminated_info = cut_first_word(termination_text)
            termination_cancel_info = record.xpath('TERMINATION_CANCEL_INFO')[0].text
            contact_info = record.xpath('CONTACTS')[0].text
            vp_dates = record.xpath('VP_DATES')[0].text
            authority = self.save_or_get_authority(record.xpath('CURRENT_AUTHORITY')[0].text)
            fop_kveds = record.xpath('ACTIVITY_KINDS')[0]
            if len(fop_kveds):
                self.add_fop_kveds_to_list(fop_kveds, code)
            exchange_data = record.xpath('EXCHANGE_DATA')[0]
            if len(exchange_data):
                self.add_exchange_data_to_list(exchange_data, code)
            if code in self.all_fops_dict:
                # TODO: make a decision: our algorithm when Fop changes fullname or address?
                fop = self.update_fop_fields(code, status, registration_date,
                                             registration_info, estate_manager, termination_date,
                                             terminated_info, termination_cancel_info,
                                             contact_info, vp_dates, authority)
                self.bulk_manager.add_update(fop)
            else:
                fop = self.create_new_fop(code, fullname, address, status, registration_date,
                                          registration_info, estate_manager, termination_date,
                                          terminated_info, termination_cancel_info, contact_info,
                                          vp_dates, authority)
                self.bulk_manager.add_create(fop)
                self.all_fops_dict[code] = fop
        if self.bulk_manager.update_queues['business_register.Fop']:
            self.bulk_manager.commit_update(Fop, ['status', 'registration_date',
                                                  'termination_date', 'terminated_info',
                                                  'termination_cancel_info', 'contact_info',
                                                  'vp_dates', 'authority'])
        if self.bulk_manager.create_queues['business_register.Fop']:
            self.bulk_manager.commit_create(Fop)
        self.save_fop_kveds_to_db()
        self.save_exchange_data_to_db()
        self.bulk_manager.update_queues['business_register.Fop'] = []
        self.bulk_manager.create_queues['business_register.Fop'] = []

    print("For storing run FopConverter().process_full()")
