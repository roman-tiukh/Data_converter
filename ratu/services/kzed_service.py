import config
from ratu.services.main import Converter
from ratu.models.kzed_models import Section, Division, Group, Kzed


class KzedConverter(Converter):
    #paths for remote and local source files
    FILE_URL = config.FILE_URL_KZED
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_KZED
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
        Section,
        Division,
        Group, 
        Kzed
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
            self.save_to_kzed_table(classes, group, division, section)


    def save_to_kzed_table (self, classes, group, division, section):
        for class_data in classes:
            kzed = Kzed()
            kzed.section = section
            kzed.division = division
            kzed.group = group
            kzed.code = class_data['classCode']
            kzed.name = class_data['className']
            kzed.save()

    
    # #storing data to all tables       
    # def save_to_db(self, data):
    #     #getting a value in json file from Ministry of justice, because is put into a list
    #     data = data['sections'][0]
    #     for data_section in data:
    #         section = Section()
    #         section.code = data_section['sectionCode']
    #         section.name = data_section['sectionName']
    #         section.save()
    #         for data_division in data_section["divisions"]:
    #             division = Division()
    #             division.section = section
    #             division.code = data_division['divisionCode']
    #             division.name = data_division['divisionName']
    #             division.save()
    #             for data_group in data_division["groups"]:
    #                 group = Group()
    #                 group.section = section
    #                 group.division = division
    #                 group.code = data_group['groupCode']
    #                 group.name = data_group['groupName']
    #                 group.save()
    #                 for data_class in data_group['classes']:
    #                     kzed = Kzed()
    #                     kzed.section = section
    #                     kzed.division = division
    #                     kzed.group = group
    #                     kzed.code = data_class['classCode']
    #                     kzed.name = data_class['className']
    #                     kzed.save()
    #     print("Saved kved data")
