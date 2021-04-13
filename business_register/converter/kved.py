import logging
from csv import DictReader

import django
import requests
from django.conf import settings
from django.utils import timezone

from business_register.models.kved_models import KvedSection, KvedDivision, KvedGroup, Kved
from data_ocean.converter import Converter
from data_ocean.downloader import Downloader
from data_ocean.models import Register

# Standard instance of a logger with __name__
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class KvedConverter(Converter):
    LOCAL_FILE_NAME = ''

    def __init__(self):
        self.API_ADDRESS_FOR_DATASET = Register.objects.get(
            source_register_id=settings.BUSINESS_KVED_SOURCE_REGISTER_ID
        ).source_api_address
        super().__init__()

    def create_kved(self, section, division, group, code, name, is_valid=True):
        Kved.objects.create(section=section, division=division, group=group, code=code,
                            name=name.lower(), is_valid=is_valid)

    # Storing default kved (there is also such migration)
    def save_default_kved(self):
        not_valid = "not_valid"
        section = KvedSection.objects.create(code=not_valid, name=not_valid)
        division = KvedDivision.objects.create(section=section, code=not_valid, name=not_valid)
        group = KvedGroup.objects.create(section=section, division=division, code=not_valid,
                                         name=not_valid)
        self.create_kved(section, division, group, not_valid, not_valid, is_valid=False)

    def save_to_section_table(self, sections):
        for section_data in sections:
            section = KvedSection.objects.create(code=section_data['sectionCode'],
                                                 name=section_data['sectionName'].lower())
            divisions = section_data['divisions']
            self.save_to_division_table(divisions, section)

    def save_to_division_table(self, divisions, section):
        for division_data in divisions:
            division = KvedDivision.objects.create(section=section,
                                                   code=division_data['divisionCode'],
                                                   name=division_data['divisionName'].lower())
            groups = division_data['groups']
            self.save_to_group_table(groups, division, section)

    def save_to_group_table(self, groups, division, section):
        for group_data in groups:
            group = KvedGroup.objects.create(section=section, division=division,
                                             code=group_data['groupCode'],
                                             name=group_data['groupName'].lower())
            classes = group_data['classes']
            self.save_to_kved_table(classes, group, division, section)

    def save_to_kved_table(self, classes, group, division, section):
        for class_data in classes:
            self.create_kved(section, division, group, class_data['classCode'],
                             class_data['className'].lower())

    # storing data to all tables
    def save_to_db(self, json_file):
        kved_not_valid = Kved.objects.filter(name='not_valid').first()
        if not kved_not_valid:
            self.save_default_kved()
        data = self.load_json(json_file)
        # getting a value from json file, because it is put into a list
        sections = data['sections'][0]
        try:
            self.save_to_section_table(sections)
        except django.db.utils.IntegrityError as e:
            logger.exception(f"Exception occurred: {e}")
            exit(1)
        else:
            logger.info("Saved all kveds")

    def save_kveds_2005_to_kved_table(self, file):
        with open(file, newline='') as csvfile:
            reader = DictReader(csvfile)
            section = KvedSection.objects.create(code='OUTDATED', name='2005')
            division = KvedDivision.objects.create(section=section, code='OUTDATED', name='2005')
            group = KvedGroup.objects.create(section=section, division=division, code='OUTDATED',
                                             name='2005')
            for row in reader:
                if (row['KV_ROZ'] and not row['KV_GR'] and not row['KV_KLAS']
                        and not row['KV_PKLAS']):
                    self.create_kved(section, division, group, row['KV_ROZ'], row['KV_NU'],
                                     is_valid=False)
                if row['KV_GR'] and not row['KV_KLAS'] and not row['KV_PKLAS']:
                    self.create_kved(section, division, group, row['KV_GR'], row['KV_NU'],
                                     is_valid=False)
                if row['KV_KLAS'] and not row['KV_PKLAS']:
                    self.create_kved(section, division, group, row['KV_KLAS'], row['KV_NU'],
                                     is_valid=False)
                if row['KV_PKLAS']:
                    self.create_kved(section, division, group, row['KV_PKLAS'], row['KV_NU'],
                                     is_valid=False)
            print('All kveds 2005 were saved')


class KvedDownloader(Downloader):
    chunk_size = 10 * 1024
    reg_name = 'business_kved'
    source_dataset_url = settings.BUSINESS_KVED_SOURCE_PACKAGE

    def get_source_file_url(self):

        r = requests.get(self.source_dataset_url)
        if r.status_code != 200:
            print(f'Request error to {self.source_dataset_url}')
            return

        for i in r.json()['result']['resources']:
            if self.zip_required_file_sign in i['url']:
                return i['url']

    def get_source_file_name(self):
        return self.url.split('/')[-1]

    def update(self):

        logger.info(f'{self.reg_name}: Update started...')

        self.report_init()
        self.download()

        self.report.update_start = timezone.now()
        self.report.save()

        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) started ...')
        KvedConverter().save_to_db(self.file_path)
        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) finished successfully.')

        self.report.update_finish = timezone.now()
        self.report.update_status = True
        self.report.save()

        self.remove_file()

        new_total_records = Kved.objects.count()
        self.update_register_field(settings.KVED_REGISTER_LIST, 'total_records', new_total_records)
        logger.info(f'{self.reg_name}: Update total records finished successfully.')

        self.measure_changes('business_register', 'Kved')
        logger.info(f'{self.reg_name}: Report created successfully.')


        logger.info(f'{self.reg_name}: Update finished successfully.')
