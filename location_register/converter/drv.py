# Drv means 'Державний реєстр виборців' - the source for the addresses data

import logging
import sys

from django.conf import settings
from django.utils import timezone
from zeep import Client, Settings
from zeep.helpers import serialize_object

from data_ocean.converter import Converter
from data_ocean.downloader import Downloader
from data_ocean.utils import clean_name, change_to_full_name
from location_register.models.drv_models import (DrvAto, DrvBuilding,
                                                 DrvCouncil, DrvDistrict,
                                                 DrvRegion, DrvStreet, ZipCode)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DrvConverter(Converter):
    WSDL_URL = settings.LOCATION_DRV_WSDL_URL
    # WSDL_URL = 'https://www.drv.gov.ua/ords/svc/personal/API/Opendata'
    SETTINGS = Settings(strict=settings.LOCATION_DRV_STRICT, xml_huge_tree=settings.LOCATION_DRV_XML_HUGE_TREE)

    # SETTINGS = Settings(strict=False, xml_huge_tree=True)

    def __init__(self):
        """
        declaring as class fields and initialising dictionaries for storing all objects from DB

        """
        self.invalid_data_counter = 0
        self.regions_dict = self.put_objects_to_dict('name', 'location_register', 'DrvRegion')
        self.districts_dict = self.put_objects_to_dict('code', 'location_register', 'DrvDistrict')
        self.outdated_districts_dict = self.put_objects_to_dict('code',
                                                                'location_register',
                                                                'DrvDistrict')
        self.councils_dict = self.put_objects_to_dict('code', 'location_register', 'DrvCouncil')
        self.outdated_councils_dict = self.put_objects_to_dict('code', 'location_register', 'DrvCouncil')
        self.atos_dict = self.put_objects_to_dict('code', 'location_register', 'DrvAto')
        self.outdated_atos_dict = self.put_objects_to_dict('code', 'location_register', 'DrvAto')
        self.streets_dict = self.put_objects_to_dict('code', 'location_register', 'DrvStreet')
        self.outdated_streets_dict = self.put_objects_to_dict('code', 'location_register', 'DrvStreet')
        self.zipcodes_dict = self.put_objects_to_dict('code', 'location_register', 'ZipCode')
        self.outdated_zipcodes_dict = self.put_objects_to_dict('code', 'location_register', 'ZipCode')
        self.outdated_buildings_list = list(DrvBuilding.objects.values_list('id', flat=True))

        super().__init__()

    def parse_regions_data(self):
        client = Client(self.WSDL_URL, service_name='GetRegionsService', settings=self.SETTINGS)
        response = client.service.GetRegions()
        # converting zeep object to Python ordered dictionary
        response_to_dict = serialize_object(response)
        # accessing a nested list with regions data as dictionaries
        return response_to_dict['Region']

    # Regions can be renamed only via constitutional amendments, so we use name as unique identifier
    # and updating only codes, numbers and short_names)
    def save_region_data(self, regions_data_list):
        for dictionary in regions_data_list:
            code = str(dictionary['Region_Id'])
            number = dictionary['Region_Num']
            name = clean_name(dictionary['Region_Name'])
            short_name = dictionary['Region_Short']
            capital = dictionary['Region_Center']
            if capital:
                capital = clean_name(capital)
            region = self.regions_dict.get(name)
            if region:
                update_fields = []
                if region.code != code:
                    region.code = code
                    update_fields.append('code')
                if region.number != number:
                    region.number = number
                    update_fields.append('number')
                if region.short_name != short_name:
                    region.short_name = short_name
                    update_fields.append('short_name')
                if update_fields:
                    update_fields.append('updated_at')
                    region.save(update_fields=update_fields)
            else:
                region = DrvRegion.objects.create(
                    code=code,
                    number=number,
                    name=name,
                    short_name=short_name,
                    capital=capital
                )
                self.regions_dict[name] = region
            atos_data_list = self.parse_atos_data(region)
            self.save_ato_data(atos_data_list, region)

    def parse_atos_data(self, region):
        client = Client(self.WSDL_URL, service_name='GetATUUService', settings=self.SETTINGS)
        response = client.service.ATUUQuery(ATOParams=region.code)
        # converting zeep object to Python ordered dictionary
        response_to_dict = serialize_object(response)
        # accessing a nested list with ATO data as dictionaries
        return response_to_dict['ATO']

    def save_ato_data(self, atos_data_list, region):
        for dictionary in atos_data_list:
            district_name = dictionary['ATO_Raj']
            district_name = change_to_full_name(district_name)
            district_name = clean_name(district_name)
            district_code = region.name + district_name
            council_name = dictionary['ATO_Rad'].lower()
            council_code = region.name + district_name + council_name
            ato_name = dictionary['ATO_Name']
            ato_name = clean_name(ato_name)
            ato_code = str(dictionary['ATO_Id'])
            district = self.districts_dict.get(district_code)
            if district:
                if self.outdated_districts_dict.get(district_code):
                    del self.outdated_districts_dict[district_code]
            else:
                district = DrvDistrict.objects.create(
                    region=region,
                    name=district_name,
                    code=district_code
                )
                self.districts_dict[district_code] = district
            council = self.councils_dict.get(council_code)
            if council:
                if self.outdated_councils_dict.get(council_code):
                    del self.outdated_councils_dict[council_code]
            else:
                council = DrvCouncil.objects.create(
                    region=region,
                    name=council_name,
                    code=council_code
                )
                self.councils_dict[council_code] = council
            ato = self.atos_dict.get(ato_code)
            if ato:
                update_fields = []
                if ato.region_id != region.id:
                    ato.region = region
                    update_fields.append('region')
                if ato.district_id != district.id:
                    ato.district = district
                    update_fields.append('district')
                if ato.council_id != council.id:
                    ato.council = council
                    update_fields.append('council')
                if ato.name != ato_name:
                    ato.name = ato_name
                    update_fields.append('name')
                if update_fields:
                    update_fields.append('updated_at')
                    ato.save(update_fields=update_fields)
                if self.outdated_atos_dict.get(ato_code):
                    del self.outdated_atos_dict[ato_code]
            else:
                ato = DrvAto.objects.create(
                    region=region,
                    district=district,
                    council=council,
                    name=ato_name,
                    code=ato_code)
                self.atos_dict[ato_code] = ato
            streets_data_list = self.parse_streets_data(ato)
            self.save_street_data(streets_data_list, region, district, council, ato)

    def parse_streets_data(self, ato):
        client = Client(self.WSDL_URL, service_name='GetAdrRegService', settings=self.SETTINGS)
        response = client.service.AdrRegQuery(AdrRegParams=ato.code)
        # converting zeep object to Python ordered dictionary
        response_to_dict = serialize_object(response)
        # accessing a nested list with ATO data as dictionaries
        return response_to_dict['GEONIM']

    def save_street_data(self, streets_data_list, region, district, council, ato):
        for dictionary in streets_data_list:
            code = str(dictionary['Geon_Id'])
            name = dictionary['Geon_Name']
            name = change_to_full_name(name)
            previous_name = dictionary['Geon_OldNames']
            if previous_name:
                previous_name = change_to_full_name(previous_name)
            buildings_info = dictionary['BUILDS']
            number_of_buildings = None
            buildings_data_list = None
            if buildings_info:
                number_of_buildings = dictionary['BUILDS']['BUILDS_COUNT']
                buildings_data_list = dictionary['BUILDS']['BUILD']
            street = self.streets_dict.get(code)
            if street:
                update_fields = []
                if street.region_id != region.id:
                    street.region = region
                    update_fields.append('region')
                if street.district_id != district.id:
                    street.district = district
                    update_fields.append('district')
                if street.council_id != council.id:
                    street.council = council
                    update_fields.append('council')
                if street.ato_id != ato.id:
                    street.ato = ato
                    update_fields.append('ato')
                if street.name != name:
                    street.name = name
                    update_fields.append('name')
                if street.previous_name != previous_name:
                    street.previous_name = previous_name
                    update_fields.append('previous_name')
                if street.number_of_buildings != number_of_buildings:
                    street.number_of_buildings = number_of_buildings
                    update_fields.append('number_of_buildings')
                if update_fields:
                    update_fields.append('updated_at')
                    street.save(update_fields=update_fields)
                if self.outdated_streets_dict.get(code):
                    del self.outdated_streets_dict[code]
            else:
                street = DrvStreet.objects.create(
                    region=region,
                    district=district,
                    council=council,
                    ato=ato,
                    code=code,
                    name=name,
                    previous_name=previous_name,
                    number_of_buildings=number_of_buildings
                )
                self.streets_dict[code] = street
            if buildings_data_list:
                self.save_building_data(buildings_data_list, region, district, council, ato, street)

    def save_building_data(self, buildings_data_list, region, district, council, ato, street):
        for dictionary in buildings_data_list:
            code = str(dictionary['Bld_ID'])
            number = dictionary['Bld_Num']
            if not number:
                # ToDo: change to None value
                number = DrvBuilding.INVALID
                self.invalid_data_counter += 1
            corps = dictionary['Bld_Korp']
            if corps:
                # uniting the building`s number and corps with '\'
                number = number + '/' + corps
            zip_code_value = dictionary['Bld_Ind']
            zip_code = self.zipcodes_dict.get(zip_code_value)
            if zip_code:
                update_fields = []
                if zip_code.region_id != region.id:
                    zip_code.region_id = region.id
                    update_fields.append('region')
                if zip_code.district_id != district.id:
                    zip_code.district_id = district.id
                    update_fields.append('district')
                if zip_code.council_id != council.id:
                    zip_code.council_id = council.id
                    update_fields.append('council')
                if zip_code.ato_id != ato.id:
                    zip_code.ato_id = ato.id
                    update_fields.append('ato')
                if update_fields:
                    update_fields.append('updated_at')
                    zip_code.save(update_fields=update_fields)
                if self.outdated_zipcodes_dict.get(zip_code_value):
                    del self.outdated_zipcodes_dict[zip_code_value]
            else:
                zip_code = ZipCode.objects.create(
                    region=region,
                    district=district,
                    council=council,
                    ato=ato,
                    code=zip_code_value)
                self.zipcodes_dict[zip_code_value] = zip_code
            building = DrvBuilding.objects.filter(code=code).first()
            if building:
                update_fields = []
                if building.region_id != region.id:
                    building.region_id = region.id
                    update_fields.append('region')
                if building.district_id != district.id:
                    building.district_id = district.id
                    update_fields.append('district')
                if building.council_id != council.id:
                    building.council_id = council.id
                    update_fields.append('council')
                if building.ato_id != ato.id:
                    building.ato_id = ato.id
                    update_fields.append('ato')
                if building.street_id != street.id:
                    building.street_id = street.id
                    update_fields.append('street')
                if building.zip_code_id != zip_code.id:
                    building.zip_code_id = zip_code.id
                    update_fields.append('zip_code')
                if building.number != number:
                    building.number = number
                    update_fields.append('number')
                if update_fields:
                    update_fields.append('updated_at')
                    building.save(update_fields=update_fields)
                self.outdated_buildings_list.remove(building.id)
            else:
                building = DrvBuilding.objects.create(
                    region=region,
                    district=district,
                    council=council,
                    ato=ato,
                    street=street,
                    zip_code=zip_code,
                    code=code,
                    number=number
                )

    def delete_outdated(self):
        if self.outdated_districts_dict:
            for district in self.outdated_districts_dict.values():
                district.soft_delete()
        if self.outdated_councils_dict:
            for council in self.outdated_councils_dict.values():
                council.soft_delete()
        if self.outdated_atos_dict:
            for ato in self.outdated_atos_dict.values():
                ato.soft_delete()
        if self.outdated_streets_dict:
            for street in self.outdated_streets_dict.values():
                street.soft_delete()
        if self.outdated_zipcodes_dict:
            for zipcode in self.outdated_zipcodes_dict.values():
                zipcode.soft_delete()
        if self.outdated_buildings_list:
            for building_id in self.outdated_buildings_list:
                DrvBuilding.objects.get(id=building_id).soft_delete()

    def process(self):
        regions_data = self.parse_regions_data()
        self.save_region_data(regions_data)
        self.delete_outdated()


class DrvUpdater(Downloader):
    reg_name = 'location_drv'
    url = settings.LOCATION_DRV_WSDL_URL
    file_name = 'there us no file - we use SOAP protocol'

    def update(self):
        logger.info(f'{self.reg_name}: Update started...')

        self.report_init()

        self.report.update_start = timezone.now()
        self.report.save()

        logger.info(f'{self.reg_name}: DrvConverter().process() started ...')
        converter = DrvConverter()
        converter.process()
        self.report.invalid_data = converter.invalid_data_counter
        logger.info(f'{self.reg_name}: DrvConverter().process() finished successfully.')

        self.report.update_finish = timezone.now()
        self.report.update_status = True
        self.report.save()

        self.vacuum_analyze(table_list=[
            'location_register_drvregion',
            'location_register_drvdistrict',
            'location_register_drvcouncil',
            'location_register_drvato',
            'location_register_drvstreet',
            'location_register_drvbuilding',

        ])

        new_total_records = DrvBuilding.objects.all().count()
        self.update_register_field(settings.DRVBUILDING_REGISTER_LIST, 'total_records', new_total_records)
        logger.info(f'{self.reg_name}: Update total records finished successfully.')

        self.measure_changes('location_register', 'DrvBuilding')
        logger.info(f'{self.reg_name}: Report created successfully.')

        logger.info(f'{self.reg_name}: Update finished successfully.')
