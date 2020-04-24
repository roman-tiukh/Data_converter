import config
from ratu.services.main import Converter
from ratu.models.kved_models import Section, Division, Group, Kved


class KvedConverter(Converter):
    #paths for remote and local source files
    FILE_URL = config.FILE_URL_KVED
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_KVED
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
        Section,
        Division,
        Group, 
        Kved
    ]

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
            self.save_to_group_table (groups, division, section)

    def save_to_group_table (self, groups, division, section):
        for group_data in groups:
            group = Group()
            group.section = section
            group.division = division
            group.code = group_data['groupCode']
            group.name = group_data['groupName']
            group.save()
            classes = group_data['classes']
            self.save_to_kved_table(classes, group, division, section)

    def save_to_kved_table (self, classes, group, division, section):
        for class_data in classes:
            kved = Kved()
            kved.section = section
            kved.division = division
            kved.group = group
            kved.code = class_data['classCode']
            kved.name = class_data['className']
            kved.save()
