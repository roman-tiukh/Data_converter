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
        region_koatuu_dict[region]=region.name
        

    #writing entry to region table 
    def save_to_region_table(self, region_data):

        level_one = 'Перший рівень'
        level_two = 'Другий рівень'
        level_three = 'Третій рівень'
        level_four = 'Четвертий рівень'
        name_object = "Назва об'єкта українською мовою"


        for index, object_koatuu in enumerate(region_data):
            for key in object_koatuu:
               if (key == level_two) & (object_koatuu[key]==''):
                    if object_koatuu[name_object] in region_koatuu_dict:
                        region = Region()
                        region.koatuu = object_koatuu[level_one]
                    #print(object_koatuu[level_one], object_koatuu[name_object])


#def save_to_district_city_table(self, data):
        #for index, object_koatuu in enumerate(region_data):
            #for key in object_koatuu:
                #if (key==level_three) & (object_koatuu[key]=='') & (object_koatuu[level_two]!=''):
                    #print(object_koatuu[level_two], object_koatuu[name_object]) 
# if (object_koatuu[self.level_two][2]=='1'):
# print('Printing objects to add to city table')
# print(object_koatuu[self.level_two], object_koatuu[self.name_object])

#if (key==level_four) & (key==level_three) & (key==level_two):
#region = Region()
#print(key, object_koatuu[key])
#if (region.koatuu is null):
#region.koatuu = object_koatuu[key]
#region.save()
#print(region.koatuu)


#if (koatuu_object[level_two] = '') & (koatuu_object[level_three] = '') & (koatuu_object[level_four] = ''): 
#koatuu_number = Region (koatuu=koatuu_object[])