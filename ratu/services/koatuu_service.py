import config
from ratu.services.main import Converter
from ratu.models.ratu_models import Region, District, City, Citydistrict

class KoatuuConverter(Converter):

    #paths for the local souce file
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_KOATUU
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #constants from json file
    LEVEL_ONE = 'Перший рівень'
    LEVEL_TWO = 'Другий рівень'
    LEVEL_THREE = 'Третій рівень'
    LEVEL_FOUR= 'Четвертий рівень'
    OBJECT_NAME = "Назва об'єкта українською мовою"

    #geting a single uppercase word from some string
    def first_word(self, string):
        string = string.upper().split()[0]
        return string

    #creating a dictionary out off the values, which already exists in ratu tables
    def create_dictionary(self, table_model):
        koatuu_dict = {} 
        for table_record in table_model.objects.all(): # dictionary for keeping whole model class objects    
            if table_record.name:
                unit_name = self.first_word(table_record.name)
                koatuu_dict[unit_name]=table_record
        return koatuu_dict                     

    #storing data to all tables
    def save_to_db(self,data):
        #getting values in json file Koatuu
        for index, object_koatuu in enumerate(data):  
            self.save_to_region_table(data, object_koatuu)
        print("Koatuu values saved")

    #writing entry to koatuu field in region table 
    def save_to_region_table(self, data, object_koatuu):
        region_koatuu_dict = self.create_dictionary(Region)             
        if (object_koatuu[self.LEVEL_ONE]!='') & (object_koatuu[self.LEVEL_TWO]==''):                
            object_region_name = object_koatuu[self.OBJECT_NAME].upper().split()[0]            
            if object_region_name in region_koatuu_dict:
                region_koatuu = region_koatuu_dict[object_region_name]
                region_koatuu.koatuu = object_koatuu[self.LEVEL_ONE]
                region_koatuu.save(update_fields=['koatuu'])