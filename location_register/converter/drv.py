# Drv means 'Державний реєстр виборців' - the source for the addresses data
import re

from zeep import Client, Settings
from zeep.helpers import serialize_object

from data_ocean.converter import Converter
from location_register.models.drv_models import (DrvAto, DrvBuilding,
                                                 DrvCouncil, DrvDistrict,
                                                 DrvRegion, DrvStreet, ZipCode)


class DrvConverter(Converter):
    WSDL_URL = 'https://www.drv.gov.ua/ords/svc/personal/API/Opendata'
    SETTINGS = Settings(strict=False, xml_huge_tree=True)
    # dictionaries and lists for storing all objects from DB
    all_regions_dict = {}
    all_atos_dict = {}
    all_zipcodes_dict = {}

    # deleting 'м.', 'смт', 'с.', 'вул.' from string 
    def clean_name(self, name):
        return re.sub(r"с\.|м\.|смт|вул.", "", name).strip()

    # changing 'р-н' to 'район'
    def change_to_full_district_name(self, name):
        return name.replace('р-н', 'район')

    # changing 'вул.' to 'вулиця ', 'бульв.' to 'бульвар ', 'пров.' to 'провулок ', 'пл.' to 'площа ', 'просп.' to 'проспект '
    def change_to_full_street_name(self, name):
        name = name.replace('вул.', 'вулиця ')        
        name = name.replace('бульв.', 'бульвар ')
        name = name.replace('просп.', 'проспект ')
        name = name.replace('пров.', 'провулок ')
        name = name.replace('пл.', 'площа ')
        return name

    def parse_regions_data(self):
        client = Client(self.WSDL_URL, service_name='GetRegionsService', settings=self.SETTINGS)
        response = client.service.GetRegions()
        # converting zeep object to Python ordered dictionary
        response_to_dict = serialize_object(response)
        # accessing a nested list with regions data as dictionaries
        return response_to_dict['Region']

    def save_region_data(self, regions_data_list):
        self.all_regions_dict = self.put_all_objects_to_dict_with_name('location_register', 'DrvRegion')
        for dictionary in regions_data_list:
            code = dictionary['Region_Id']
            number = dictionary['Region_Num']
            name = dictionary['Region_Name']
            name = self.clean_name(name)
            short_name = dictionary['Region_Short']
            capital = dictionary['Region_Center']
            if capital:
                capital = self.clean_name(capital)
            if name in self.all_regions_dict:
                region = self.all_regions_dict[name]
                region.code = code
                region.number = number
                region.short_name = short_name
                region.capital = capital
            else:
                region = DrvRegion(code=code, number=number, name=name, short_name=short_name, capital=capital)
                self.all_regions_dict[name] = region
            region.save()
            print(f'Дані регіону {region.name} збережено')
            atos_data_list = self.parse_atos_data(region)
            self.save_ato_data(atos_data_list, region)
    
    def parse_atos_data(self, region):
        client = Client(self.WSDL_URL, service_name='GetATUUService', settings=self.SETTINGS)
        response = client.service.ATUUQuery(ATOParams=region.code)
        # converting zeep object to Python ordered dictionary
        response_to_dict = serialize_object(response)
        # accessing a nested list with ATO data as dictionaries
        return(response_to_dict['ATO'])

    def save_ato_data(self, atos_data_list, region):
        self.all_atos_dict = self.put_all_objects_to_dict_with_code('location_register', 'DrvAto')
        for dictionary in atos_data_list:
            district_name = dictionary['ATO_Raj']
            district_name =  self.change_to_full_district_name(district_name)
            district_name =  self.clean_name(district_name)
            council_name = dictionary['ATO_Rad']
            ato_name = dictionary['ATO_Name']
            ato_name = self.clean_name(ato_name)
            # converting an integer value to string for comparing with codes from DB that are strings 
            ato_code = str(dictionary['ATO_Id'])
            district = DrvDistrict.objects.filter(region=region, name=district_name).first()
            if not district:
                district = DrvDistrict(region=region, name=district_name)
                district.save()
            council = DrvCouncil.objects.filter(region=region, name=council_name).first()
            if not council:
                council = DrvCouncil(region=region, name=council_name)
                council.save()
            if ato_code in self.all_atos_dict:
                ato = self.all_atos_dict[ato_code]
                ato.region=region
                ato.district=district
                ato.council=council
                ato.name = ato_name
            else:
                ato = DrvAto(region=region, district=district, council=council, name=ato_name, code=ato_code)
                self.all_atos_dict[ato_code] = ato
            ato.save()
            print(f'Дані населеного пункту {ato.name} збережено')
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
            # converting an integer value to string for comparing with codes from DB that are strings 
            code = str(dictionary['Geon_Id'])
            name = dictionary['Geon_Name']
            name =  self.change_to_full_street_name(name)
            previous_name = dictionary['Geon_OldNames']
            if previous_name:
                previous_name = self.change_to_full_street_name(previous_name)
            buildings_info = dictionary['BUILDS']
            number_of_buildings = None
            buildings_data_list =  None
            if buildings_info:
                number_of_buildings = dictionary['BUILDS']['BUILDS_COUNT']
                buildings_data_list = dictionary['BUILDS']['BUILD']
            street = DrvStreet.objects.filter(code=code).first()
            if not street:
                street = DrvStreet(region=region, 
                                district=district, 
                                council=council, 
                                ato=ato, 
                                code=code, 
                                name=name, 
                                previous_name=previous_name, 
                                number_of_buildings=number_of_buildings)
            else:
                street.name = name
                street.previous_name = previous_name
                street.number_of_buildings = number_of_buildings
            street.save()
            if buildings_data_list:
                self.save_building_data(buildings_data_list, region, district, council, ato, street)

    def save_building_data(self, buildings_data_list, region, district, council, ato, street):
        self.all_zipcodes_dict =  self.put_all_objects_to_dict_with_code('location_register', 'ZipCode')
        for dictionary in buildings_data_list:
            # converting an integer value to string for comparing with codes from DB that are strings
            code = str(dictionary['Bld_ID'])
            number = dictionary['Bld_Num']
            if not number:
                number = DrvBuilding.INVALID
            corps = dictionary['Bld_Korp']
            if corps:
                # uniting the building`s number and corps with '\'
                number = number +'/' + corps
            zipcode = dictionary['Bld_Ind']
            if zipcode in self.all_zipcodes_dict:
                zipcode = self.all_zipcodes_dict[zipcode]
            else:
                zipcode = ZipCode(region=region, district=district, council=council, ato=ato, code=zipcode)
                zipcode.save()
                self.all_zipcodes_dict[zipcode.code] = zipcode
            building = DrvBuilding.objects.filter(code=code).first()
            if not building:
                building = DrvBuilding(region=region, 
                                district=district, 
                                council=council, 
                                ato=ato, 
                                street=street,
                                zip_code=zipcode,
                                code=code, 
                                number=number)
            else:
                building.number = number
                building.zipcode=zipcode
            building.save()

    def process(self):
        regions_data = self.parse_regions_data()
        self.save_region_data(regions_data)

    print("For storing run DrvConverter().process()")