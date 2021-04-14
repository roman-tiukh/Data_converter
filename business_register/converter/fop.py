import logging
from time import sleep
import re
import requests
from django.utils import timezone
from data_ocean.downloader import Downloader
from business_register.converter.business_converter import BusinessConverter
from business_register.models.fop_models import (ExchangeDataFop, Fop,
                                                 FopToKved)
from django.conf import settings
from data_ocean.converter import BulkCreateManager
from data_ocean.models import Register
from data_ocean.utils import get_first_word, cut_first_word, format_date_to_yymmdd
from stats.tasks import endpoints_cache_warm_up

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FopConverter(BusinessConverter):

    def __init__(self):
        self.API_ADDRESS_FOR_DATASET = Register.objects.get(source_register_id=
                                                            "1c7f3815-3259-45e0-bdf1-64dca07ddc10").source_api_address
        self.LOCAL_FOLDER = settings.LOCAL_FOLDER
        self.LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_FOP
        self.CHUNK_SIZE = settings.CHUNK_SIZE_FOP
        self.RECORD_TAG = 'RECORD'
        self.bulk_manager = BulkCreateManager()
        self.new_fops_foptokveds = {}
        self.new_fops_exchange_data = {}
        super().__init__()

    def add_fop_kveds_to_dict(self, fop_kveds_from_record, code):
        all_fop_foptokveds = []
        for activity in fop_kveds_from_record:
            code_info = activity.xpath('CODE')
            if not code_info:
                continue
            kved_code = code_info[0].text
            if not kved_code:
                continue
            name_info = activity.xpath('NAME')
            if not name_info:
                continue
            kved_name = name_info[0].text
            if not kved_name:
                continue
            kved = self.get_kved_from_DB(kved_code, kved_name)
            is_primary = activity.xpath('PRIMARY')[0].text == "так"
            fop_to_kved = FopToKved(kved=kved, primary_kved=is_primary)
            all_fop_foptokveds.append(fop_to_kved)
        if len(all_fop_foptokveds):
            self.new_fops_foptokveds[code] = all_fop_foptokveds

    # putting all kveds into a list
    def update_fop_kveds(self, fop_kveds_from_record, fop):
        already_stored_foptokveds = list(FopToKved.objects.filter(fop=fop))
        for activity in fop_kveds_from_record:
            code_info = activity.xpath('CODE')
            if not code_info:
                continue
            kved_code = code_info[0].text
            if not kved_code:
                continue
            name_info = activity.xpath('NAME')
            if not name_info:
                continue
            kved_name = name_info[0].text
            if not kved_name:
                continue
            kved = self.get_kved_from_DB(kved_code, kved_name)
            is_primary = activity.xpath('PRIMARY')[0].text == "так"
            alredy_stored = False
            if len(already_stored_foptokveds):
                for stored_foptokved in already_stored_foptokveds:
                    if (stored_foptokved.kved.code == kved.code
                            and stored_foptokved.kved.name == kved.name):
                        alredy_stored = True
                        if stored_foptokved.primary_kved != is_primary:
                            stored_foptokved.primary_kved = is_primary
                            stored_foptokved.save(update_fields=['primary_kved', 'updated_at'])
                        already_stored_foptokveds.remove(stored_foptokved)
                        break
            if not alredy_stored:
                fop_to_kved = FopToKved(fop=fop, kved=kved, primary_kved=is_primary)
                self.bulk_manager.add(fop_to_kved)
        if len(already_stored_foptokveds):
            for outdated_foptokved in already_stored_foptokveds:
                outdated_foptokved.soft_delete()

    def extract_exchange_data(self, answer):
        authority_info = answer.xpath('AUTHORITY_NAME')
        authority = None
        if authority_info and authority_info[0].text:
            authority = self.save_or_get_authority(authority_info[0].text)
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
        if end_number_info and end_number_info[0].text:
            end_number = end_number_info[0].text
        return authority, taxpayer_type, start_date, start_number, end_date, end_number

    def add_fop_exchange_data_to_dict(self, exchange_data, code):
        all_fop_exchangedata = []
        for answer in exchange_data:
            authority, taxpayer_type, start_date, start_number, end_date, end_number \
                = self.extract_exchange_data(answer)
            if (not authority and not taxpayer_type and not start_date
                    and not start_number and not end_date and not end_number):
                continue
            exchange_data = ExchangeDataFop(authority=authority, taxpayer_type=taxpayer_type,
                                            start_date=start_date, start_number=start_number,
                                            end_date=end_date, end_number=end_number)
            all_fop_exchangedata.append(exchange_data)
        if len(all_fop_exchangedata):
            self.new_fops_exchange_data[code] = all_fop_exchangedata

    # putting all exchange data into a list
    def update_fop_exchange_data(self, exchange_data, fop):
        already_stored_exchange_data = ExchangeDataFop.objects.filter(fop=fop)
        for answer in exchange_data:
            authority, taxpayer_type, start_date, start_number, end_date, end_number \
                = self.extract_exchange_data(answer)
            if (not authority and not taxpayer_type and not start_date
                    and not start_number and not end_date and not end_number):
                continue
            already_stored = False
            for stored_exchange_data in already_stored_exchange_data:
                # ToDo: find way to check dates
                if (stored_exchange_data.authority == authority
                        and stored_exchange_data.taxpayer_type == taxpayer_type
                        and stored_exchange_data.start_number == start_number
                        and stored_exchange_data.end_number == end_number):
                    already_stored = True
                    break
            if not already_stored:
                exchange_data = ExchangeDataFop(fop=fop, authority=authority,
                                                taxpayer_type=taxpayer_type,
                                                start_date=start_date, start_number=start_number,
                                                end_date=end_date, end_number=end_number)
                self.bulk_manager.add(exchange_data)

    def save_detailed_fop_to_db(self, records):
        for record in records:
            fullname = record.xpath('NAME')[0].text
            if not fullname:
                logger.warning(f'ФОП без прізвища: {record}')
                self.report.invalid_data += 1
                continue
            if len(fullname) > 100:
                logger.warning(f'ФОП із задовгим прізвищем: {record}')
                continue
            if fullname:
                fullname = fullname.lower()
            address = record.xpath('ADDRESS')[0].text
            if not address:
                address = 'EMPTY'
            code = fullname + address
            status = self.save_or_get_status(record.xpath('STAN')[0].text)
            registration_text = record.xpath('REGISTRATION')[0].text
            # first getting date, then registration info if REGISTRATION.text exists
            registration_date = None
            registration_info = None
            if registration_text:
                registration_date = format_date_to_yymmdd(get_first_word(registration_text))
                registration_info = cut_first_word(registration_text)
            estate_manager = record.xpath('ESTATE_MANAGER')[0].text
            termination_text = record.xpath('TERMINATED_INFO')[0].text
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
            exchange_data = record.xpath('EXCHANGE_DATA')[0]
            fop = Fop.objects.filter(code=code).first()
            if not fop:
                fop = Fop(
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
                    authority=authority,
                    code=code)
                self.bulk_manager.add(fop)
                if len(fop_kveds):
                    self.add_fop_kveds_to_dict(fop_kveds, code)
                if len(exchange_data):
                    self.add_fop_exchange_data_to_dict(exchange_data, code)
            else:
                # TODO: make a decision: our algorithm when Fop changes fullname or address?
                update_fields = []
                if fop.status != status:
                    fop.status = status
                    update_fields.append('status')
                if fop.registration_date and str(fop.registration_date) != registration_date:
                    fop.registration_date = registration_date
                    update_fields.append('registration_date')
                if fop.registration_info != registration_info:
                    fop.registration_info = registration_info
                    update_fields.append('registration_info')
                if fop.estate_manager != estate_manager:
                    fop.estate_manager = estate_manager
                    update_fields.append('estate_manager')
                if fop.termination_date and str(fop.termination_date) != termination_date:
                    fop.termination_date = termination_date
                    update_fields.append('termination_date')
                if fop.terminated_info != terminated_info:
                    fop.terminated_info = terminated_info
                    update_fields.append('terminated_info')
                if fop.termination_cancel_info != termination_cancel_info:
                    fop.termination_cancel_info = termination_cancel_info
                    update_fields.append('termination_cancel_info')
                if fop.contact_info != contact_info:
                    fop.contact_info = contact_info
                    update_fields.append('contact_info')
                if fop.vp_dates != vp_dates:
                    fop.vp_dates = vp_dates
                    update_fields.append('vp_dates')
                if fop.authority != authority:
                    fop.authority = authority
                    update_fields.append('authority')
                if len(update_fields):
                    update_fields.append('updated_at')
                    fop.save(update_fields=update_fields)
                if len(fop_kveds):
                    self.update_fop_kveds(fop_kveds, fop)
                if len(exchange_data):
                    self.update_fop_exchange_data(exchange_data, fop)
        if len(self.bulk_manager.queues['business_register.Fop']):
            self.bulk_manager.commit(Fop)
        for fop in self.bulk_manager.queues['business_register.Fop']:
            if fop.code not in self.new_fops_foptokveds:
                continue
            foptokveds = self.new_fops_foptokveds[fop.code]
            for foptokved in foptokveds:
                foptokved.fop = fop
                self.bulk_manager.add(foptokved)
        self.new_fops_foptokveds = {}
        for fop in self.bulk_manager.queues['business_register.Fop']:
            if fop.code not in self.new_fops_exchange_data:
                continue
            fop_exchangedata = self.new_fops_exchange_data[fop.code]
            for exchangedata in fop_exchangedata:
                exchangedata.fop = fop
                self.bulk_manager.add(exchangedata)
        self.new_fops_exchange_data = {}
        self.bulk_manager.queues['business_register.Fop'] = []
        if len(self.bulk_manager.queues['business_register.FopToKved']):
            self.bulk_manager.commit(FopToKved)
        if len(self.bulk_manager.queues['business_register.ExchangeDataFop']):
            self.bulk_manager.commit(ExchangeDataFop)
        self.bulk_manager.queues['business_register.FopToKved'] = []
        self.bulk_manager.queues['business_register.ExchangeDataFop'] = []

    def save_or_update_kved(self, kved, fop):
        current_fop_to_kved = FopToKved.objects.filter(
            fop=fop,
            kved=kved
        ).first()
        if not current_fop_to_kved:
            FopToKved.objects.create(
                fop=fop,
                kved=kved,
                primary_kved=True
            )
        else:
            if not current_fop_to_kved.primary_kved:
                current_fop_to_kved.primary_kved = True
                current_fop_to_kved.save(update_fields=['primary_kved', 'updated_at'])

    def save_to_db(self, records):
        for record in records:
            fullname = record.xpath('FIO')[0].text
            if not fullname:
                logger.warning(f'ФОП без прізвища: {record}')
                self.report.invalid_data += 1
                continue
            if len(fullname) > 100:
                logger.warning(f'ФОП із задовгим прізвищем: {record}')
                continue
            fullname = fullname.lower()
            address = record.xpath('ADDRESS')[0].text
            if not address:
                address = 'EMPTY'
            code = fullname + address
            status = self.save_or_get_status(record.xpath('STAN')[0].text)
            fop = Fop.objects.filter(code=code).first()
            if not fop:
                fop = Fop.objects.create(
                    fullname=fullname,
                    address=address,
                    status=status,
                    code=code)
            else:
                # TODO: make a decision: our algorithm when Fop changes fullname or address?
                update_fields = []
                if fop.status != status:
                    fop.status = status
                    update_fields.append('status')
                if len(update_fields):
                    update_fields.append('updated_at')
                    fop.save(update_fields=update_fields)
            kved_data = record.xpath('KVED')[0].text
            if kved_data and ' ' in kved_data:
                kved = self.extract_kved(kved_data)
                self.save_or_update_kved(kved, fop)

    print("For storing run FopConverter().process()")


class FopDownloader(Downloader):
    chunk_size = 16 * 1024 * 1024
    reg_name = 'business_fop'
    zip_required_file_sign = re.compile(r'UFOP_[0-3]')
    unzip_required_file_sign = 'EDR_FOP'
    unzip_after_download = True
    source_dataset_url = settings.BUSINESS_FOP_SOURCE_PACKAGE

    def get_source_file_url(self):

        r = requests.get(self.source_dataset_url)
        if r.status_code != 200:
            print(f'Request error to {self.source_dataset_url}')
            return

        for i in r.json()['result']['resources']:
            # 17-ufop_25-11-2020.zip       <---
            # 17-ufop_full_07-08-2020.zip
            if re.search(self.zip_required_file_sign, i['name']):
                return i['url']

    def get_source_file_name(self):
        return self.url.split('/')[-1]

    def update(self):

        logger.info(f'{self.reg_name}: Update started...')

        self.report_init()
        self.download()

        self.report.update_start = timezone.now()
        self.report.save()

        logger.info(f'{self.reg_name}: process() with {self.file_path} started ...')
        fop = FopConverter()
        fop.LOCAL_FILE_NAME = self.file_name
        sleep(5)
        fop.process()
        logger.info(f'{self.reg_name}: process() with {self.file_path} finished successfully.')

        self.report.update_finish = timezone.now()
        self.report.update_status = True
        self.report.save()

        sleep(5)
        self.vacuum_analyze(table_list=['business_register_fop', ])

        self.remove_file()
        endpoints_cache_warm_up(endpoints=['/api/fop/'])
        new_total_records = Fop.objects.count()
        self.update_register_field(settings.FOP_REGISTER_LIST, 'total_records', new_total_records)
        logger.info(f'{self.reg_name}: Update total records finished successfully.')

        self.measure_changes('business_register', 'Fop')
        logger.info(f'{self.reg_name}: Report created successfully.')

        logger.info(f'{self.reg_name}: Update finished successfully.')
