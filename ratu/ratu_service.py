import ratu.config as config
from ratu.models.ratu_models import Region, District, City, Citydistrict, Street
from ratu.services import Converter

class Ratu(Converter):
    
    #paths for remote and local source files
    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME
    LOCAL_FOLDER = config.LOCAL_FOLDER

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
 
    #creating lists for registration items that had writed to db 
    region_list = []
    district_list = list()
    city_list = list()
    citydistrict_list = list()
    
    #writing entry to db
    def save_to_db(self, record):
        self.save_to_region_table(record)
        self.save_to_district_table(record)
        self.save_to_city_table(record)
        self.save_to_citydistrict_table(record)
        self.save_to_street_table(record)
        print('saved')
    
    #writing entry to region table           
    def save_to_region_table(self, record):
        if not record['OBL_NAME'] in self.region_list:
            global region
            region = Region(
                name=record['OBL_NAME']
                )
            region.save()
            self.region_list.insert(0, record['OBL_NAME'])
            region=Region.objects.get(
                name=record['OBL_NAME']
                )
    
    #writing entry to district table    
    def save_to_district_table(self, record):
        if record['REGION_NAME']:
            a=record['REGION_NAME']
        else:
            a=District.EMPTY_FIELD
        if not [region, a] in self.district_list:
            global district
            district = District(
                region=region, 
                name=a
                )
            district.save()
            self.district_list.insert(0, [region, a])
            district=District.objects.get(
                name=a,
                region=district.region
                )

    #writing entry to city table    
    def save_to_city_table(self, record):
        if record['CITY_NAME']:
            b=record['CITY_NAME']
        else:
            b=City.EMPTY_FIELD 
        if not [region, district, b] in self.city_list:
            global city
            city = City(
                region=region, 
                district=district,
                name=b
                )
            city.save()
            self.city_list.insert(0, [region, district, b])
            city=City.objects.get(
                name=b,
                region=district.region,
                district=city.district
            )
    
    #writing entry to citydistrict table
    def save_to_citydistrict_table(self, record):
        if record['CITY_REGION_NAME']:
            c=record['CITY_REGION_NAME']
        else:
            c=Citydistrict.EMPTY_FIELD
        if not [region, district, city, c] in self.citydistrict_list:
            global citydistrict
            citydistrict = Citydistrict(
                region=region, 
                district=district,
                city=city,
                name=c
                )
            citydistrict.save()
            self.citydistrict_list.insert(0, [region, district, city, c])
            citydistrict=Citydistrict.objects.get(
                name=c,
                region=district.region,
                district=city.district,
                city=citydistrict.city
                )
    
    #writing entry to street table
    def save_to_street_table(self, record):    
        street = Street(
            region=region, 
            district=district,
            city=city,
            citydistrict=citydistrict,
            name=record['STREET_NAME']
            )
        try:
            street.save()
        except:
            None
       
    print('Ratu already imported. For start rewriting to the DB run > Ratu().process()')