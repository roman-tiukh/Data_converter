import ratu.config as config
from ratu.models.ratu_models import Region, District, City, Citydistrict, Street
from ratu.services import Converter

class Ratu(Converter):
    
    #paths for remote and local sours files
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
        'RECORD': [],
        'OBL_NAME': [],
        'REGION_NAME': [],
        'CITY_NAME': [],
        'CITY_REGION_NAME': [],
        'STREET_NAME': []
    }
 
    #creating lists for registration items that had writed to db 
    region_list = []
    district_list = list()
    city_list = list()
    citydistrict_list = list()
    
    def save_to_db(self, record):
               
        #writing entry to region table
        if not record['OBL_NAME'][0] in self.region_list:
            global region
            region = Region(
                name=record['OBL_NAME'][0]
                )
            region.save()
            self.region_list.insert(0, record['OBL_NAME'][0])
            region=Region.objects.get(name=record['OBL_NAME'][0])

        if record['REGION_NAME'][0]:
            a=record['REGION_NAME'][0]
        else:
            a=District.EMPTY_FIELD
        #writing entry to district table
        if not [region, a] in self.district_list:
            global district
            district = District(
                region=region, 
                name=a
                )
            district.save()
            self.district_list.insert(0, [region, a])
            district=District.objects.get(name=a, region=district.region)

        if record['CITY_NAME'][0]:
            b=record['CITY_NAME'][0]
        else:
            b=City.EMPTY_FIELD
        #writing entry to city table
        if not [region, district, b] in self.city_list:
            global city
            city = City(
                region=region, 
                district=district,
                name=b
                )
            city.save()
            self.city_list.insert(0, [region, district, b])
            city=City.objects.get(name=b, region=district.region, district=city.district)

        if record['CITY_REGION_NAME'][0]:
            c=record['CITY_REGION_NAME'][0]
        else:
            c=Citydistrict.EMPTY_FIELD
        
        #writing entry to citydistrict table
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
            citydistrict=Citydistrict.objects.get(name=c, region=district.region, district=city.district, city=citydistrict.city)
        
        #writing entry to street table
        street = Street(
            region=region, 
            district=district,
            city=city,
            citydistrict=citydistrict,
            name=record['STREET_NAME'][0]
            )
        try:
            street.save()
        except:
            None
        print('saved')
    print('Ratu already imported. For start rewriting to the DB run > Ratu().process()')