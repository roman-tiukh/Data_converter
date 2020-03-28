import ratu.config as config
from ratu.services import Converter
from ratu.models.ratu_models import Region, District, City, Citydistrict, Street

class Ratu(Converter):
    print('1')
    
    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME
    LOCAL_FOLDER = config.LOCAL_FOLDER

    def save_to_db(self, data):
        print('2')

        #clearing all db tables        
        Region.objects.all().delete()
        District.objects.all().delete()
        City.objects.all().delete()
        Citydistrict.objects.all().delete()
        Street.objects.all().delete()
        
        #creating lists for registration items that had writed to db 
        region_list = []
        district_list = list()
        city_list = list()
        citydistrict_list = list()

        #iteration fo records in .xml file
        for record in data['DATA']['RECORD']:

            print('.')
            
            #writing entry to region table
            if not record['OBL_NAME'] in region_list:
                region = Region(
                    name=record['OBL_NAME']
                    )
                region.save()
                region_list.insert(0, record['OBL_NAME'])
                region=Region.objects.get(name=record['OBL_NAME'])

            if record['REGION_NAME']:
                a=record['REGION_NAME']
            else:
                a=District.EMPTY_FIELD
            #writing entry to district table
            if not [region, a] in district_list:
                district = District(
                    region=region, 
                    name=a
                    )
                district.save()
                district_list.insert(0, [region, a])
                district=District.objects.get(name=a, region=district.region)

            if record['CITY_NAME']:
                b=record['CITY_NAME']
            else:
                b=City.EMPTY_FIELD
            #writing entry to city table
            if not [region, district, b] in city_list:
                city = City(
                    region=region, 
                    district=district,
                    name=b
                    )
                city.save()
                city_list.insert(0, [region, district, b])
                city=City.objects.get(name=b, region=district.region, district=city.district)

            if record['CITY_REGION_NAME']:
                c=record['CITY_REGION_NAME']
            else:
                c=Citydistrict.EMPTY_FIELD
            
            #writing entry to citydistrict table
            if not [region, district, city, c] in citydistrict_list:
                citydistrict = Citydistrict(
                    region=region, 
                    district=district,
                    city=city,
                    name=c
                    )
                citydistrict.save()
                citydistrict_list.insert(0, [region, district, city, c])
                citydistrict=Citydistrict.objects.get(name=c, region=district.region, district=city.district, city=citydistrict.city)
            
            #writing entry to street table
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