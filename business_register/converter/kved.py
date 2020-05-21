from business_register.models.kved_models import Section, Division, Group, Kved
from data_ocean.converter import Converter


class KvedConverter(Converter):
    LOCAL_FILE_NAME = "kved.json"
    DATASET_ID = "e1afb81c-70e4-4009-96a0-b240c36e4603"

    # list of models for clearing DB
    tables = [
        Section,
        Division,
        Group,
        Kved
    ]

    # We can delete this function after changing clear_db function in Converter
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

    # #storing data to all tables
    def save_to_db(self, data):
        # getting a value from json file, because it is put into a list
        sections = data['sections'][0]
        self.save_to_section_table(sections)
        print("Saved kved data ")

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