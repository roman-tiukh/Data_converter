from django.conf import settings

from data_ocean.converter import Converter
from location_register.models.ratu_models import Region, District, City, Citydistrict, Category


class KoatuuConverter(Converter):

    # paths for the local souce file
    LOCAL_FILE_NAME = settings.LOCATION_KOATUU_LOCAL_FILE_NAME

    # constants from json file
    LEVEL_ONE = 'Перший рівень'
    LEVEL_TWO = 'Другий рівень'
    LEVEL_THREE = 'Третій рівень'
    LEVEL_FOUR = 'Четвертий рівень'
    CATEGORY = 'Категорія'
    OBJECT_NAME = "Назва об'єкта українською мовою"

    # geting all words before virgule and changing string to lowercase
    def get_lowercase_words_before_virgule(self, string):
        return string.lower().split('/')[0]

    # creating a dictionary out off the values, which already exists in region table
    def create_dictionary_for(self, table_model):# table_medel is one model from ratu_models
        koatuu_dict = {}
        table_model_objects = table_model.objects.all()
        for table_record in table_model_objects: # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating a dictionary out off the values, which already exists in city table
    def create_dictionary_for_city_table(self, table_model):
        koatuu_dict = {}
        table_model_objects = table_model.objects.all() # table_model is a model from ratu_models
        for table_record in table_model_objects: # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name + str(table_record.district_id)
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating a dictionary out off the values, which already exists in district y city table
    def create_dictionary_for_district_table(self, table_model):
        koatuu_dict = {}
        table_model_objects = table_model.objects.all() # table_model is a model from ratu_models
        for table_record in table_model_objects: # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name + str(table_record.region_id)
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating a dictionary out off the values, which already exists in citydistrict table
    def create_dictionary_for_citydistrict_table(self):# table_model is a model from ratu_models
        koatuu_dict = {}
        table_model_objects = Citydistrict.objects.all()
        for table_record in table_model_objects: # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name + str(table_record.city_id)
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating list out of name and district_id from json file for district items
    def create_district_items_list(self, object_region_name, region_dict, \
        object_district_name, koatuu_value):
        district_items_list = []
        if not object_region_name in region_dict:
            return
        region_koatuu = region_dict[object_region_name]
        if not koatuu_value[:2] == str(region_koatuu.koatuu)[:2]:
            return
        object_district_name = object_district_name + str(region_koatuu.id)
        district_items_list.append(object_district_name)
        return district_items_list

    # creating list out of name and district_id from json file fot city items
    def create_city_items_list(self, city_dict, district_items_list, koatuu_value):
        city_list = []
        for object_district_name in district_items_list:
            if (object_district_name in city_dict) & (koatuu_value[2] == '1'):
                city_koatuu = city_dict[object_district_name]
                city_list.append(city_koatuu.name + str(city_koatuu.district_id))
            return city_list

    # getting id value from category table
    def get_category_id(self, string):
        if string == '':
            id_number = Category.objects.get(name='null').id
        else:
            id_number = Category.objects.get(name=string).id
        return id_number

    # storing data to all tables
    def save_to_db(self, data):
        self.save_to_region_table(data)
        self.save_to_district_table(data)
        self.save_to_city_or_citydistrict(data)
        self.writing_category_null_id(City)
        self.writing_category_null_id(Citydistrict)
        print("Koatuu values saved")

    # writing entry to koatuu field in region table
    def save_to_region_table(self, data):
        for index, object_koatuu in enumerate(data):
            region_dict = self.create_dictionary_for(Region)
            if (object_koatuu[self.LEVEL_ONE] != '') & (object_koatuu[self.LEVEL_TWO] == ''):
                object_region_name = self.get_lowercase_words_before_virgule \
                    (object_koatuu[self.OBJECT_NAME])
                if  not object_region_name in region_dict:
                    return
                region_koatuu = region_dict[object_region_name]
                region_koatuu.koatuu = object_koatuu[self.LEVEL_ONE]
                region_koatuu.save()
        print("Koatuu values to region saved")

    # writing entry to koatuu field in district table and level_two records of city_table
    def save_to_district_table(self, data):
        region_dict = self.create_dictionary_for(Region)
        district_dict = self.create_dictionary_for_district_table(District)
        city_dict = self.create_dictionary_for_city_table(City)
        for index, object_koatuu in enumerate(data):
            if (object_koatuu[self.LEVEL_ONE] != '') & (object_koatuu[self.LEVEL_TWO] == ''):
                object_region_name = self.get_lowercase_words_before_virgule \
                    (object_koatuu[self.OBJECT_NAME])
            if (object_koatuu[self.LEVEL_ONE] != '') & (object_koatuu[self.LEVEL_TWO] != '') & \
                (object_koatuu[self.LEVEL_THREE] == ''):
                # koatuu_value is position in koatuu number wich defines district or city record
                koatuu_value = str(object_koatuu[self.LEVEL_TWO])
                object_district_name = self.get_lowercase_words_before_virgule \
                    (object_koatuu[self.OBJECT_NAME])
                district_items_list = self.create_district_items_list \
                    (object_region_name, region_dict, object_district_name, koatuu_value)
                category_level_two = self.get_category_id(object_koatuu[self.CATEGORY])
                for object_district_name in district_items_list:
                    if (object_district_name in district_dict) & (koatuu_value[2] != '1'):
                        district_koatuu = district_dict[object_district_name]
                        district_koatuu.koatuu = object_koatuu[self.LEVEL_TWO]
                        district_koatuu.save()
                    elif (object_district_name in city_dict) & (koatuu_value[2] == '1'):
                        city_koatuu = city_dict[object_district_name]
                        city_koatuu.koatuu = object_koatuu[self.LEVEL_TWO]
                        city_koatuu.category_id = category_level_two
                        city_koatuu.save()
        print("Koatuu values to district saved")

    # processing entry to koatuu field in city_table and citydistrict_table
    def save_to_city_or_citydistrict(self, data):
        region_dict = self.create_dictionary_for(Region)
        district_dict = self.create_dictionary_for_district_table(District)
        city_dict_for_district_table = self.create_dictionary_for_district_table(City)
        city_dict = self.create_dictionary_for_city_table(City)
        citydistrict_dict = self.create_dictionary_for_citydistrict_table()
        # getting values in json file Koatuu
        for index, object_koatuu in enumerate(data):
            if (object_koatuu[self.LEVEL_ONE] != '') & (object_koatuu[self.LEVEL_TWO] == ''):
                object_region_name = self.get_lowercase_words_before_virgule \
                    (object_koatuu[self.OBJECT_NAME])
            if (object_koatuu[self.LEVEL_ONE] != '') & (object_koatuu[self.LEVEL_TWO] != '') & \
                (object_koatuu[self.LEVEL_THREE] == ''):
                # koatuu_value is position in koatuu number wich defines district or city record
                koatuu_value = str(object_koatuu[self.LEVEL_TWO])
                object_district_name = self.get_lowercase_words_before_virgule \
                    (object_koatuu[self.OBJECT_NAME])
                district_items_list = self.create_district_items_list \
                    (object_region_name, region_dict, object_district_name, koatuu_value)
                city_items_list = self.create_city_items_list \
                    (city_dict_for_district_table, district_items_list, koatuu_value)
            if (object_koatuu[self.LEVEL_ONE] != '') & (object_koatuu[self.LEVEL_TWO] != '') & \
                (object_koatuu[self.LEVEL_THREE] != '') & (object_koatuu[self.LEVEL_FOUR] == ''):
                object_city_name = self.get_lowercase_words_before_virgule(
                    object_koatuu[self.OBJECT_NAME])
                object_level_three = object_koatuu[self.LEVEL_THREE]
                category_level_three = self.get_category_id(object_koatuu[self.CATEGORY])
                self.save_to_city_or_citydistrict_table(
                    object_level_three,
                    object_city_name,
                    district_items_list,
                    district_dict,
                    city_dict,
                    category_level_three)
                self.save_to_city_or_citydistrict_table(
                    object_level_three,
                    object_city_name,
                    city_items_list,
                    city_dict,
                    citydistrict_dict,
                    category_level_three)
            if (object_koatuu[self.LEVEL_ONE] != '') & (object_koatuu[self.LEVEL_TWO] != '') & \
                (object_koatuu[self.LEVEL_THREE] != '') & (object_koatuu[self.LEVEL_FOUR] != ''):
                object_citydistrict_name = self.get_lowercase_words_before_virgule(
                    object_koatuu[self.OBJECT_NAME])
                object_level_four = object_koatuu[self.LEVEL_FOUR]
                category_level_four = self.get_category_id(object_koatuu[self.CATEGORY])
                self.save_to_city_or_citydistrict_table(
                    object_level_four,
                    object_citydistrict_name,
                    district_items_list,
                    district_dict,
                    city_dict,
                    category_level_four)
                self.save_to_city_or_citydistrict_table(
                    object_level_four,
                    object_citydistrict_name,
                    city_items_list,
                    city_dict,
                    citydistrict_dict,
                    category_level_four)
        print("Koatuu values to city and citydistrict saved")

    # writing entry to koatuu field in city and citydistrict table
    def save_to_city_or_citydistrict_table(self, object_level_number, object_level_name, \
        level_items_list, up_level_dict, level_dict, category):
        for object_name in level_items_list:
            if not object_name in up_level_dict:
                return
            up_level_koatuu = up_level_dict[object_name]
            if str(object_level_number)[:5] != str(up_level_koatuu.koatuu)[:5]:
                return
            object_level_name = object_level_name + str(up_level_koatuu.id)
            if not object_level_name in level_dict:
                return
            level_koatuu = level_dict[object_level_name]
            level_koatuu.koatuu = object_level_number
            level_koatuu.category_id = category
            level_koatuu.save()

    # writing entry to category fields where koatuu is empty
    def writing_category_null_id(self, table_model):
        category = self.get_category_id('null')
        table_model_objects = table_model.objects.filter(category_id__isnull=True).count()
        for table_record in table_model_objects:
            table_record.category_id = category
            table_record.save()
