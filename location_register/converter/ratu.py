import logging

import requests
from django.conf import settings
from django.utils import timezone

from data_ocean.converter import Converter, BulkCreateManager
from data_ocean.downloader import Downloader
from data_ocean.models import Register
from data_ocean.utils import clean_name, change_to_full_name
from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ToDo: define how to mark outdated records
class RatuConverter(Converter):
    def __init__(self):
        self.API_ADDRESS_FOR_DATASET = Register.objects.get(
            source_register_id=settings.LOCATION_RATU_SOURCE_REGISTER_ID
        ).source_api_address
        self.LOCAL_FOLDER = settings.LOCAL_FOLDER
        self.LOCAL_FILE_NAME = settings.LOCAL_FILE_NAME_RATU
        self.CHUNK_SIZE = settings.CHUNK_SIZE_RATU
        self.RECORD_TAG = 'RECORD'
        self.bulk_manager = BulkCreateManager()
        self.all_regions_dict = self.put_all_objects_to_dict('name', 'location_register',
                                                             'RatuRegion')
        self.all_districts_dict = self.put_all_objects_to_dict('code', 'location_register',
                                                               'RatuDistrict')
        self.all_cities_dict = self.put_all_objects_to_dict('code', 'location_register',
                                                            'RatuCity')
        self.all_citydistricts_dict = self.put_all_objects_to_dict('code', 'location_register',
                                                                   'RatuCityDistrict')
        self.all_streets_dict = self.put_all_objects_to_dict('code', 'location_register',
                                                             'RatuStreet')
        super().__init__()

    def rename_file(self, file):
        new_filename = file
        if file.upper().find('ATU') >= 0:
            new_filename = 'ratu.xml'
        return new_filename

    def save_or_get_region(self, name):
        region_name = clean_name(name)
        region_name = change_to_full_name(region_name)
        if region_name not in self.all_regions_dict:
            region = RatuRegion.objects.create(
                name=region_name
            )
            self.all_regions_dict[region_name] = region
            return region
        return self.all_regions_dict[region_name]

    def save_or_get_district(self, name, region):
        district_name = clean_name(name)
        district_name = change_to_full_name(district_name)
        district_code = region.name + district_name
        if district_code not in self.all_districts_dict:
            district = RatuDistrict.objects.create(
                region=region,
                name=district_name,
                code=district_code
            )
            self.all_districts_dict[district_code] = district
            return district
        return self.all_districts_dict[district_code]

    def save_or_get_city(self, name, region, district):
        city_name = clean_name(name)
        district_name = 'EMPTY' if not district else district.name
        city_code = region.name + district_name + city_name
        if city_code not in self.all_cities_dict:
            city = RatuCity.objects.create(
                region=region,
                district=district,
                name=city_name,
                code=city_code
            )
            self.all_cities_dict[city_code] = city
            return city
        return self.all_cities_dict[city_code]

    def save_or_get_citydistrict(self, name, region, district, city):
        citydistrict_name = clean_name(name)
        citydistrict_code = city.name + citydistrict_name
        if citydistrict_code not in self.all_citydistricts_dict:
            citydistrict = RatuCityDistrict.objects.create(
                region=region,
                district=district,
                city=city,
                name=citydistrict_name,
                code=citydistrict_code
            )
            self.all_citydistricts_dict[citydistrict_code] = citydistrict
            return citydistrict
        return self.all_citydistricts_dict[citydistrict_code]

    def save_street(self, name, region, district, city, citydistrict):
        street_name = change_to_full_name(name)
        # Saving streets that are located in Kyiv and Sevastopol that are regions
        if not city:
            city = self.save_or_get_city(region.name, region, district)
        street_code = city.name + street_name
        if street_code not in self.all_streets_dict:
            street = RatuStreet.objects.create(
                region=region,
                district=district,
                city=city,
                citydistrict=citydistrict,
                name=street_name,
                code=street_code
            )

    def save_to_db(self, records):
        for record in records:
            region = self.save_or_get_region(record.xpath('OBL_NAME')[0].text)
            district = (self.save_or_get_district(record.xpath('REGION_NAME')[0].text, region)
                        if record.xpath('REGION_NAME')[0].text else None)
            city = (self.save_or_get_city(record.xpath('CITY_NAME')[0].text, region, district)
                    if record.xpath('CITY_NAME')[0].text else None)
            citydistrict = (self.save_or_get_citydistrict(record.xpath('CITY_REGION_NAME')[0].text,
                                                          region, district, city)
                            if record.xpath('CITY_REGION_NAME')[0].text else None)
            if record.xpath('STREET_NAME')[0].text:
                self.save_street(record.xpath('STREET_NAME')[0].text, region, district,
                                 city, citydistrict)

    print(
        'RatuConverter already imported.',
        'For start rewriting RATU to the DB run > RatuConverter().process()'
    )


class RatuDownloader(Downloader):
    chunk_size = 16 * 1024 * 1024
    reg_name = 'location_ratu'
    zip_required_file_sign = 'xml_atu'
    unzip_required_file_sign = 'xml_atu'
    unzip_after_download = True
    source_dataset_url = settings.LOCATION_RATU_SOURCE_PACKAGE

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

        logger.info(f'{self.reg_name}: process() with {self.file_path} started ...')
        ratu = RatuConverter()
        ratu.LOCAL_FILE_NAME = self.file_name
        ratu.process()
        logger.info(f'{self.reg_name}: process() with {self.file_path} finished successfully.')

        self.log_obj.update_finish = timezone.now()
        self.log_obj.update_status = True
        self.log_obj.save()

        self.remove_file()

        logger.info(f'{self.reg_name}: Update finished successfully.')
