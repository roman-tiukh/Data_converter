import logging
import django

from django.conf import settings
from business_register.models.kved_models import Section, Division, Group, Kved
from data_ocean.converter import Converter
from data_ocean.models import Register

# Standard instance of a logger with __name__
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class KvedConverter(Converter):
    LOCAL_FILE_NAME = "kved.json"

    def __init__(self):
        self.API_ADDRESS_FOR_DATASET = Register.objects.get(
            source_register_id=settings.LOCATION_KVED_SOURCE_REGISTER_ID
            ).api_address
        super().__init__()

    # Storing default kved (there is also such migration)
    def save_default_kved(self):
        section = Section()
        section.code = "EMP"
        section.name = "EMPTY"
        section.save()

        division = Division()
        division.section = section
        division.code = "EMP"
        division.name = "EMPTY"
        division.save()

        group = Group()
        group.section = section
        group.division = division
        group.code = "EMP"
        group.name = "EMPTY"
        group.save()

        kved = Kved()
        kved.section = section
        kved.division = division
        kved.group = group
        kved.code = "EMP"
        kved.name = "EMPTY"
        kved.save()

    def save_to_section_table(self, sections):
        for section_data in sections:
            section = Section()
            section.code = section_data['sectionCode']
            section.name = section_data['sectionName']
            section.save()
            divisions = section_data['divisions']
            self.save_to_division_table(divisions, section)

    def save_to_division_table(self, divisions, section):
        for division_data in divisions:
            division = Division()
            division.section = section
            division.code = division_data['divisionCode']
            division.name = division_data['divisionName']
            division.save()
            groups = division_data['groups']
            self.save_to_group_table(groups, division, section)

    def save_to_group_table(self, groups, division, section):
        for group_data in groups:
            group = Group()
            group.section = section
            group.division = division
            group.code = group_data['groupCode']
            group.name = group_data['groupName']
            group.save()
            classes = group_data['classes']
            self.save_to_kved_table(classes, group, division, section)

    def save_to_kved_table(self, classes, group, division, section):
        for class_data in classes:
            kved = Kved()
            kved.section = section
            kved.division = division
            kved.group = group
            kved.code = class_data['classCode']
            kved.name = class_data['className']
            kved.save()

    # storing data to all tables
    def save_to_db(self, data):
        # getting a value from json file, because it is put into a list
        sections = data['sections'][0]
        logger.info("Saved all kveds")
        try:
            self.save_to_section_table(sections)
        except django.db.utils.IntegrityError:
            logger.exception("Exception occurred")
        else:
            logger.info("Saved all kveds")
