import codecs
import io
from ratu.models.ratu_models import Region, District, City, Citydistrict, Street
import requests
import sys
import xmltodict
import zipfile

#pip freeze > requirements.txt - must run after add or change import modules

class Converter:

    print('3')

    def __init__(self):
        return 

    def unzip_file(self):
        # getting zip file  from FILE_URL & extracting to LOCAL_FOLDER
        try:
            r = requests.get(self.FILE_URL)
        except TimeoutError as err:   
            print ("Error open zip file " + self.FILE_URL)
            return 
        zip_file = zipfile.ZipFile(io.BytesIO(r.content))
        zip_file.extractall(self.LOCAL_FOLDER)
            
    def parse_file(self):
        # encoding & parsing .xml source file
        with codecs.open(self.LOCAL_FOLDER + self.LOCAL_FILE_NAME, encoding="cp1251") as file:
            return xmltodict.parse(file.read()) 
                
    def process(self): #writing .xml data to db

        print('4')

        data=self.parse_file()
        self.save_to_db(data)
        
    # -------------- end of process()