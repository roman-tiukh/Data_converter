import codecs
import io
import requests
import xmltodict
import zipfile
from service import Service
import config
#pip freeze > requirements.txt - must run after add or change import modules

class Converter(Service):

    FILE_URL = config.FILE_URL
    LOCAL_FILE_NAME = config.LOCAL_FILE_NAME
    LOCAL_FOLDER = config.LOCAL_FOLDER

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
        # encoding & parsing LOCAL_FILE_NAME
        with codecs.open(self.LOCAL_FOLDER + self.LOCAL_FILE_NAME, encoding="cp1251") as file:
            data = xmltodict.parse(file.read()) 
        return data
        
    def process(data):
        # @TODO: Ivan add your code here
        None
        
data = Converter()
data.unzip_file()
#data.parse_file()