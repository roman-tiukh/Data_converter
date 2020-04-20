import config
from ratu.services.main import Converter
from ratu.models.kzed_models import Section, Division, Group #, Kzed


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
        # Kzed
    ]
    
    # hope I will not need that
    # #format record's data
    # record={
    #     'sectionCode': '',
    #     'sectionName': '',
    #     'divisionCode': '',
    #     'divisionName': '',
    #     'groupCode': '',
    #     'groupName': '',
    #     'classCode': '',
    #     'className': '',
    # }

    # hope I will not need that
    # dictionaries for keeping all model class objects
    # section_dict={} 
    # division_dict={}
    # group_dict={}
    # kzed_dict={}

    #storing data to all tables       
    def save_to_db(self, data):
        data = data['sections'][0]
        for data_section in data:
            section = Section()
            section.code = data_section['sectionCode']
            section.name = data_section['sectionName']
            section.save()
            for data_division in data_section["divisions"]:
                division = Division()
                division.section = section
                division.code = data_division['divisionCode']
                division.name = data_division['divisionName']
                division.save()
                for data_group in data_division["groups"]:
                    group = Group()
                    group.section = section
                    group.division = division
                    group.code = data_group['groupCode']
                    group.name = data_group['groupName']
                    group.save()
                    #add one for for storing Kzed
        print("saved")
