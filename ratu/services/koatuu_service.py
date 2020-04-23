import config
from ratu.services.main import Converter
from ratu.models.ratu_models import Region, District, City, Citydistrict

class KoatuuConverter(Converter):

    #paths for remote and local souce files
    #FILE_URL = config.FILE_URL
    #LOCAL_FILE_NAME = config.LOCAL_FILE_NAME_KOATUU
    LOCAL_FOLDER = config.LOCAL_FOLDER

    #list of models for clearing DB
    tables=[
    Region,
    District,
    City,
    Citydistrict
    ]

    #creating dictionary & lists for registration items that had writed to db 
    region_koatuu_dict = {} # dictionary uses for keeping whole model class objects    

    for region in Region.objects.all():

        if region.name:
            region_name = region.name.upper().split()[0]
            region_koatuu_dict[region_name]=region
         
    #writing entry to koatuu field in region table 
    def save_to_region_table(self, data):
        for index, object_koatuu in enumerate(data):            
            if (object_koatuu['Перший рівень']!='') & (object_koatuu['Другий рівень']==''):                
                object_region_name = object_koatuu["Назва об'єкта українською мовою"].upper().split()[0]            
                if object_region_name in self.region_koatuu_dict:
                    region_koatuu = self.region_koatuu_dict[object_region_name]
                    region_koatuu.koatuu = object_koatuu['Перший рівень']
                    region_koatuu.save(update_fields=['koatuu'])                   