import config
from data_ocean.models.ratu_models import Region, District, City, Citydistrict, Street
from data_ocean.services.main import Converter, BulkCreateManager
import re


class RatuConverter(Converter):
    
    #paths for remote and local source files
    FILE_URL = "https://data.gov.ua/dataset/75e57837-128b-49e1-a007-5e7dfa7bf6af/resource/e21a1e57-051c-46ea-9c8e-8f30de7d863d/download/"
    DOWNLOADED_FILE_NAME = "ratu.zip"
    LOCAL_FILE_NAME = "ratu.xml"
    CHUNK_SIZE = 200

    #list of models for clearing DB
    tables=[
        Region,
        District,
        City,
        Citydistrict,
        Street
    ]
    
    #format record's data
    record={
        'RECORD': '',
        'OBL_NAME': '',
        'REGION_NAME': '',
        'CITY_NAME': '',
        'CITY_REGION_NAME': '',
        'STREET_NAME': ''
    }
 
    def rename (self, file):
        new_filename = ""
        if (file.upper().find('ATU') >= 0): new_filename = 'ratu.xml'
        return new_filename
    
    #creating dictionary & lists for registration items that had writed to db
    region_dict = {} # dictionary uses for keeping whole model class objects
    district_list = list() # lists use for keeping cells content
    city_list = list()
    citydistrict_list = list()

    bulk_manager = BulkCreateManager(CHUNK_SIZE)

    #changing from records like: "волинська обл." to "волинська область"
    def clean_region_name(self, region):
        region = region.lower()
        region = re.sub(r"обл\.", "область", region)
        return region.strip()

    #changing from records like: "донецький р-н" to "донецький район", "р.райони вінницької області" to "райони вінницької області", "райони міста Київ" to "райони м.Київ"
    def clean_district_name(self, district):
        district = district.lower()
        district = re.sub(r"р-н", "район", district)
        district = re.sub(r"р\.", "", district)
        district = re.sub(r"райони міста", "райони м.", district)
        district = re.sub(r"области", "області", district) #fixing up particular mistake in data
        return district.strip()

    #changing from records like: "с.високе" to "високе", "м.судак" to "судак", "смт.научне" to "научне", "сщ.стальне" to "стальне", "с/рада.вілінська" to "вілінська", "сщ/рада.поштівська" to "поштівська"
    def clean_city_or_citydistrict_name(self, city):
        city = city.lower()
        city = re.sub(r"с\.", "", city)
        city = re.sub(r"м\.", "", city)
        city = re.sub(r"р\.", "", city)
        city = re.sub(r"смт\.", "", city)
        city = re.sub(r"сщ\.", "", city)
        city = re.sub(r"с/рада\.", "", city)
        city = re.sub(r"сщ/рада\.", "", city)
        return city.strip()
    
    #writing entry to db
    def save_to_db(self, record):
        region=self.save_to_region_table(record)
        district=self.save_to_district_table(record, region)
        city=self.save_to_city_table(record,region, district)
        citydistrict=self.save_to_citydistrict_table(record, region, district, city)
        self.save_to_street_table(record,region, district, city, citydistrict)
        print('saved')
    
    #writing entry to region table
    def save_to_region_table(self, record):
        record['OBL_NAME'] = self.clean_region_name(record['OBL_NAME'])
        if not record['OBL_NAME'] in self.region_dict:
            region = Region(
                name=record['OBL_NAME']
                )
            region.save()
            self.region_dict[record['OBL_NAME']]=region
            return region
        region=self.region_dict[record['OBL_NAME']]
        return region
    
    #writing entry to district table
    def save_to_district_table(self, record, region):
        if record['REGION_NAME']:
            district_name = self.clean_district_name(record['REGION_NAME'])
        else:
            district_name=District.EMPTY_FIELD
        if not [region.id, district_name] in self.district_list:
            district = District(
                region=region, 
                name=district_name
                )
            district.save()
            self.district_list.insert(0, [region.id, district_name])
        district=District.objects.get(
            name=district_name,
            region=region.id
            )
        return district

    #writing entry to city table
    def save_to_city_table(self, record, region, district):
        if record['CITY_NAME']:
            city_name = self.clean_city_or_citydistrict_name(record['CITY_NAME'])
        else:
            city_name=City.EMPTY_FIELD
        if not [region.id, district.id, city_name] in self.city_list:
            city = City(
                region=region, 
                district=district,
                name=city_name
                )
            city.save()
            self.city_list.insert(0, [region.id, district.id, city_name])
        city=City.objects.get(
            name=city_name,
            region=region.id,
            district=district.id
            )
        return city
    
    #writing entry to citydistrict table
    def save_to_citydistrict_table(self, record, region, district, city):
        if record['CITY_REGION_NAME']:
            citydistrict_name = self.clean_city_or_citydistrict_name(record['CITY_REGION_NAME'])
        else:
            citydistrict_name=Citydistrict.EMPTY_FIELD
        if not [region.id, district.id, city.id, citydistrict_name] in self.citydistrict_list:
            citydistrict = Citydistrict(
                region=region,
                district=district,
                city=city,
                name=citydistrict_name
                )
            citydistrict.save()
            self.citydistrict_list.insert(0, [region.id, district.id, city.id, citydistrict_name])
        citydistrict=Citydistrict.objects.get(
            name=citydistrict_name,
            region=region.id,
            district=district.id,
            city=city.id
            )
        return citydistrict
    
    #writing entry to street table
    def save_to_street_table(self, record, region, district, city, citydistrict):
        if record['STREET_NAME']:
            street = Street(
                region=region, 
                district=district,
                city=city,
                citydistrict=citydistrict,
                name=record['STREET_NAME'].lower()
                )
            self.bulk_manager.add(street)
       
    print(
        'Ratu already imported. For start rewriting RATU to the DB run > RatuConverter().process()\n',
        'For clear all RATU tables run > RatuConverter().clear_db()'
        )