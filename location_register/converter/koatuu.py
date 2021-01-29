# Python logging package
import logging
from django.conf import settings
from django.utils import timezone
import requests
from data_ocean.converter import Converter
from data_ocean.downloader import Downloader
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict
from location_register.models.koatuu_models import (KoatuuFirstLevel, KoatuuSecondLevel, KoatuuThirdLevel,
                                                    KoatuuFourthLevel, KoatuuCategory)
from data_ocean.utils import clean_name, change_to_full_name, get_lowercase_substring_before_slash

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    def create_dictionary_for(self, table_model):  # table_medel is one model from ratu_models
        koatuu_dict = {}
        table_model_objects = table_model.objects.all()
        for table_record in table_model_objects:  # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating a dictionary out off the values, which already exists in city table
    def create_dictionary_for_city_table(self, table_model):
        koatuu_dict = {}
        table_model_objects = table_model.objects.all()  # table_model is a model from ratu_models
        for table_record in table_model_objects:  # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name + str(table_record.district_id)
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating a dictionary out off the values, which already exists in district y city table
    def create_dictionary_for_district_table(self, table_model):
        koatuu_dict = {}
        table_model_objects = table_model.objects.all()  # table_model is a model from ratu_models
        for table_record in table_model_objects:  # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name + str(table_record.region_id)
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating a dictionary out off the values, which already exists in citydistrict table
    def create_dictionary_for_citydistrict_table(self):  # table_model is a model from ratu_models
        koatuu_dict = {}
        table_model_objects = RatuCityDistrict.objects.all()
        for table_record in table_model_objects:  # dictionary for keeping whole model class objects
            if table_record.name:
                unit_name = table_record.name + str(table_record.city_id)
                koatuu_dict[unit_name] = table_record
        return koatuu_dict

    # creating list out of name and district_id from json file for district items
    def create_district_items_list(
            self,
            object_region_name,
            region_dict,
            object_district_name,
            koatuu_value
    ):
        district_items_list = []
        if object_region_name not in region_dict:
            return
        region_koatuu = region_dict[object_region_name]
        if koatuu_value[:2] != str(region_koatuu.koatuu)[:2]:
            return
        object_district_name = object_district_name + str(region_koatuu.id)
        district_items_list.append(object_district_name)
        return district_items_list

    # creating list out of name and district_id from json file fot city items
    def create_city_items_list(self, city_dict, district_items_list, koatuu_value):
        city_list = []
        for object_district_name in district_items_list:
            if object_district_name in city_dict and koatuu_value[2] == '1':
                city_koatuu = city_dict[object_district_name]
                city_list.append(city_koatuu.name + str(city_koatuu.district_id))
            return city_list

    # getting id value from category table
    def get_category_id(self, string):
        id_number = KoatuuCategory.objects.get(code=string).id
        return id_number

    # writing entry to koatuu field in region table
    def save_to_region_table(self, data):
        region_dict = self.create_dictionary_for(RatuRegion)
        for object_koatuu in data:
            if object_koatuu[self.LEVEL_ONE] and not object_koatuu[self.LEVEL_TWO]:
                object_region_name = self.get_lowercase_words_before_virgule(
                    object_koatuu[self.OBJECT_NAME])
                if object_region_name not in region_dict:
                    return
                region_koatuu = region_dict[object_region_name]
                region_koatuu.koatuu = object_koatuu[self.LEVEL_ONE]
                region_koatuu.save()
        logger.info("Koatuu values to region saved")

    # writing entry to koatuu field in district table and level_two records of city_table
    def save_to_district_table(self, data):
        region_dict = self.create_dictionary_for(RatuRegion)
        district_dict = self.create_dictionary_for_district_table(RatuDistrict)
        city_dict = self.create_dictionary_for_city_table(RatuCity)
        for object_koatuu in data:
            if object_koatuu[self.LEVEL_ONE] and not object_koatuu[self.LEVEL_TWO]:
                object_region_name = self.get_lowercase_words_before_virgule(
                    object_koatuu[self.OBJECT_NAME])
            if object_koatuu[self.LEVEL_ONE] and object_koatuu[
                self.LEVEL_TWO] and not object_koatuu[self.LEVEL_THREE]:
                # koatuu_value is position in koatuu number wich defines district or city record
                koatuu_value = str(object_koatuu[self.LEVEL_TWO])
                object_district_name = self.get_lowercase_words_before_virgule(
                    object_koatuu[self.OBJECT_NAME])
                district_items_list = self.create_district_items_list(
                    object_region_name, region_dict, object_district_name, koatuu_value)
                category_level_two = self.get_category_id(object_koatuu[self.CATEGORY])
                for object_district_name in district_items_list:
                    if (object_district_name in district_dict) and (koatuu_value[2] != '1'):
                        district_koatuu = district_dict[object_district_name]
                        district_koatuu.koatuu = object_koatuu[self.LEVEL_TWO]
                        district_koatuu.save()
                    elif (object_district_name in city_dict) and (koatuu_value[2] == '1'):
                        city_koatuu = city_dict[object_district_name]
                        city_koatuu.koatuu = object_koatuu[self.LEVEL_TWO]
                        city_koatuu.category_id = category_level_two
                        city_koatuu.save()
        logger.info("Koatuu values to district saved")

    # processing entry to koatuu field in city_table and citydistrict_table
    def save_to_city_or_citydistrict(self, data):
        region_dict = self.create_dictionary_for(RatuRegion)
        district_dict = self.create_dictionary_for_district_table(RatuDistrict)
        city_dict_for_district_table = self.create_dictionary_for_district_table(RatuCity)
        city_dict = self.create_dictionary_for_city_table(RatuCity)
        citydistrict_dict = self.create_dictionary_for_citydistrict_table()
        # getting values in json file Koatuu
        for object_koatuu in data:
            if object_koatuu[self.LEVEL_ONE] and not object_koatuu[self.LEVEL_TWO]:
                object_region_name = self.get_lowercase_words_before_virgule(
                    object_koatuu[self.OBJECT_NAME])
            if object_koatuu[self.LEVEL_ONE] and object_koatuu[
                self.LEVEL_TWO] and not object_koatuu[self.LEVEL_THREE]:
                # koatuu_value is position in koatuu number wich defines district or city record
                koatuu_value = str(object_koatuu[self.LEVEL_TWO])
                object_district_name = self.get_lowercase_words_before_virgule(
                    object_koatuu[self.OBJECT_NAME])
                district_items_list = self.create_district_items_list(
                    object_region_name, region_dict, object_district_name, koatuu_value)
                city_items_list = self.create_city_items_list(
                    city_dict_for_district_table, district_items_list, koatuu_value)
            if object_koatuu[self.LEVEL_ONE] and object_koatuu[self.LEVEL_TWO] and object_koatuu[
                self.LEVEL_THREE] and not object_koatuu[self.LEVEL_FOUR]:
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
                    category_level_three
                )
                self.save_to_city_or_citydistrict_table(
                    object_level_three,
                    object_city_name,
                    city_items_list,
                    city_dict,
                    citydistrict_dict,
                    category_level_three
                )
            if object_koatuu[self.LEVEL_ONE] and object_koatuu[self.LEVEL_TWO] and object_koatuu[
                self.LEVEL_THREE] and not object_koatuu[self.LEVEL_FOUR]:
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
                    category_level_four
                )
                self.save_to_city_or_citydistrict_table(
                    object_level_four,
                    object_citydistrict_name,
                    city_items_list,
                    city_dict,
                    citydistrict_dict,
                    category_level_four
                )
        logger.info("Koatuu values to city and citydistrict saved")

    # writing entry to koatuu field in city and citydistrict table
    def save_to_city_or_citydistrict_table(
            self,
            object_level_number,
            object_level_name,
            level_items_list,
            up_level_dict,
            level_dict,
            category
    ):
        for object_name in level_items_list:
            if object_name not in up_level_dict:
                return
            up_level_koatuu = up_level_dict[object_name]
            if str(object_level_number)[:5] != str(up_level_koatuu.koatuu)[:5]:
                return
            object_level_name = object_level_name + str(up_level_koatuu.id)
            if object_level_name not in level_dict:
                return
            level_koatuu = level_dict[object_level_name]
            level_koatuu.koatuu = object_level_number
            level_koatuu.category_id = category
            level_koatuu.save()

    # writing entry to category fields where koatuu is empty
    def writing_category_null_id(self, table_model):
        category = self.get_category_id('null')
        table_model_objects = table_model.objects.filter(category_id__isnull=True)
        for table_record in table_model_objects:
            table_record.category_id = category
            table_record.save()

    # storing data to all tables
    def save_to_db(self, json_file):
        data = self.load_json(json_file)
        try:
            self.save_to_region_table(data)
            self.save_to_district_table(data)
            self.save_to_city_or_citydistrict(data)
            self.writing_category_null_id(RatuCity)
            self.writing_category_null_id(RatuCityDistrict)
        except TypeError:
            logger.exception('Tried to iterate NonType object')
        else:
            logger.info("Koatuu values saved")


class NewKoatuuConverter(Converter):

    def __init__(self):
        self.LOCAL_FILE_NAME = settings.LOCATION_KOATUU_LOCAL_FILE_NAME
        self.all_first_level_places = self.put_all_objects_to_dict('code', 'location_register',
                                                                   'KoatuuFirstLevel')
        self.all_second_level_places = self.put_all_objects_to_dict('code', 'location_register',
                                                                    'KoatuuSecondLevel')
        self.all_third_level_places = self.put_all_objects_to_dict('code', 'location_register',
                                                                   'KoatuuThirdLevel')
        self.all_fourth_level_places = self.put_all_objects_to_dict('code', 'location_register',
                                                                    'KoatuuFourthLevel')
        self.all_categories = self.put_all_objects_to_dict('code', 'location_register',
                                                           'KoatuuCategory')
        # a dictionary for storing all abbreviations and full forms of KOATUU categories
        self.KOATUU_CATEGORY_DICT = {
            'С': 'село',
            'Щ': 'селище',
            'Т': 'селище міського типу ',
            'М': 'місто',
            'Р': 'район міста'
        }
        self.TRANSLITERATION_DICT = {
            'C': 'С',
            'T': 'Т',
            'M': 'М',
            'P': 'Р'
        }

    def transliterate_to_ukr(self, category_code):
        if category_code in self.TRANSLITERATION_DICT:
            return self.TRANSLITERATION_DICT.get(category_code)
        return category_code

    def save_or_get_category(self, category_code):
        category_code = self.transliterate_to_ukr(category_code)
        if category_code not in self.all_categories:
            name = self.KOATUU_CATEGORY_DICT[category_code]
            category = KoatuuCategory.objects.create(name=name, code=category_code)
            self.all_categories[category_code] = category
        return self.all_categories[category_code]

    def save_or_update_first_level(self, name, first_level_code):
        if first_level_code not in self.all_first_level_places:
            first_level = KoatuuFirstLevel.objects.create(name=name, code=first_level_code)
            self.all_first_level_places[first_level_code] = first_level
            logger.warning(f'Збережено новий регіон у КОАТУУ із назвою: {name}')
        else:
            first_level = self.all_first_level_places[first_level_code]
            if first_level.name != name:
                logger.warning(f'Не збігаються код або назва регіону у КОАТУУ: {first_level}')

    def save_or_update_second_level(self, first_level_code, category, name, second_level_code):
        first_level = self.all_first_level_places[first_level_code]
        if second_level_code not in self.all_second_level_places:
            second_level = KoatuuSecondLevel.objects.create(first_level=first_level,
                                                            category=category,
                                                            name=name,
                                                            code=second_level_code)
            self.all_second_level_places[second_level_code] = second_level
        else:
            second_level = self.all_second_level_places[second_level_code]
            update_fields = []
            if second_level.first_level != first_level:
                second_level.first_level = first_level
                update_fields.append('first_level')
            if second_level.category != category:
                second_level.category = category
                update_fields.append('category')
            if second_level.name != name:
                second_level.name = name
                update_fields.append('name')
            if len(update_fields):
                update_fields.append('updated_at')
                second_level.save(update_fields=update_fields)

    def save_or_update_third_level(self, first_level_code, second_level_code, category, name,
                                   third_level_code):
        first_level = self.all_first_level_places[first_level_code]
        second_level = self.all_second_level_places[second_level_code]
        if third_level_code not in self.all_third_level_places:
            third_level = KoatuuThirdLevel.objects.create(first_level=first_level,
                                                          second_level=second_level,
                                                          category=category,
                                                          name=name,
                                                          code=third_level_code)
            self.all_third_level_places[third_level_code] = third_level
        else:
            third_level = self.all_third_level_places[third_level_code]
            update_fields = []
            if third_level.first_level != first_level:
                third_level.first_level = first_level
                update_fields.append('first_level')
            if third_level.second_level != second_level:
                third_level.second_level = second_level
                update_fields.append('second_level')
            if third_level.category != category:
                third_level.category = category
                update_fields.append('category')
            if third_level.name != name:
                third_level.name = name
                update_fields.append('name')
            if len(update_fields):
                update_fields.append('updated_at')
                third_level.save(update_fields=update_fields)

    def save_or_update_fourth_level(self, first_level_code, second_level_code, third_level_code,
                                    category, name, fourth_level_code):
        first_level = self.all_first_level_places[first_level_code]
        second_level = self.all_second_level_places[second_level_code]
        third_level = self.all_third_level_places[third_level_code]
        if fourth_level_code not in self.all_fourth_level_places:
            fourth_level = KoatuuFourthLevel.objects.create(first_level=first_level,
                                                            second_level=second_level,
                                                            third_level=third_level,
                                                            category=category,
                                                            name=name, code=fourth_level_code)
            self.all_fourth_level_places[fourth_level_code] = fourth_level
        else:
            fourth_level = self.all_fourth_level_places[fourth_level_code]
            update_fields = []
            if fourth_level.first_level != first_level:
                fourth_level.first_level = first_level
                update_fields.append('first_level')
            if fourth_level.second_level != second_level:
                fourth_level.second_level = second_level
                update_fields.append('second_level')
            if fourth_level.third_level != third_level:
                fourth_level.third_level = third_level
                update_fields.append('third_level')
            if fourth_level.category != category:
                fourth_level.category = category
                update_fields.append('category')
            if fourth_level.name != name:
                fourth_level.name = name
                update_fields.append('name')
            if len(update_fields):
                update_fields.append('updated_at')
                fourth_level.save(update_fields=update_fields)

    def save_to_db(self, json_file):
        data = self.load_json(json_file)
        for object_koatuu in data:
            first_level_code = object_koatuu['Перший рівень']
            # checking that all codes are strings, not integers that happens
            if not isinstance(first_level_code, str):
                first_level_code = str(first_level_code)
            second_level_code = object_koatuu['Другий рівень']
            if not isinstance(second_level_code, str):
                second_level_code = str(second_level_code)
            third_level_code = object_koatuu['Третій рівень']
            if not isinstance(third_level_code, str):
                third_level_code = str(third_level_code)
            fourth_level_code = object_koatuu['Четвертий рівень']
            if not isinstance(fourth_level_code, str):
                fourth_level_code = str(fourth_level_code)
            category_code = object_koatuu['Категорія']
            category = None
            if category_code:
                category = self.save_or_get_category(category_code)
            name = object_koatuu["Назва об'єкта українською мовою"]
            if first_level_code and not second_level_code:
                name = clean_name(
                    get_lowercase_substring_before_slash(name)
                )
                self.save_or_update_first_level(name, first_level_code)
                continue
            if first_level_code and second_level_code and not third_level_code:
                name = change_to_full_name(
                    clean_name(
                        get_lowercase_substring_before_slash(name))
                )
                self.save_or_update_second_level(first_level_code, category, name,
                                                 second_level_code)
                continue
            if (first_level_code and second_level_code and third_level_code and
                    not fourth_level_code):
                name = change_to_full_name(
                    clean_name(
                        get_lowercase_substring_before_slash(name))
                )
                self.save_or_update_third_level(first_level_code, second_level_code, category,
                                                name, third_level_code)
                continue
            if (first_level_code and second_level_code and third_level_code and
                    fourth_level_code):
                # omitting the incorrect record from data.gov.ua
                # ToDo: get explanation from the government
                if third_level_code == '2320381000':
                    logger.warning(f'Код третього рівня не існує в json: {object_koatuu}')
                    continue
                name = name.lower()
                self.save_or_update_fourth_level(first_level_code, second_level_code,
                                                 third_level_code, category, name,
                                                 fourth_level_code)


class KoatuuDownloader(Downloader):
    chunk_size = 10 * 1024
    reg_name = 'location_koatuu'
    source_dataset_url = settings.LOCATION_KOATUU_SOURCE_PACKAGE

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

        self.log_init()
        self.download()

        self.log_obj.update_start = timezone.now()
        self.log_obj.save()

        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) started ...')
        NewKoatuuConverter().save_to_db(self.file_path)
        logger.info(f'{self.reg_name}: save_to_db({self.file_path}) finished successfully.')

        self.log_obj.update_finish = timezone.now()
        self.log_obj.update_status = True
        self.log_obj.save()

        self.remove_file()

        logger.info(f'{self.reg_name}: Update finished successfully.')
