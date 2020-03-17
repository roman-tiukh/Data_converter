import codecs
import io
import requests
import xmltodict
import zipfile
from service import Service

class Converter(Service):

    FILE_URL = "https://data.gov.ua/dataset/75e57837-128b-49e1-a007-5e7dfa7bf6af/resource/e21a1e57-051c-46ea-9c8e-8f30de7d863d/download/28-ex_xml_atu.zip"
    LOCAL_FILE_NAME = "28-ex_xml_atu.xml"
    LOCAL_FOLDER = "unzipped_xml"

    def __init__(self):
        return 

    def unzip_file(self):
        # getting zip file  from FILE_URL & extracting to LOCAL_FOLDER
        r = requests.get(self.FILE_URL)
        zip_file = zipfile.ZipFile(io.BytesIO(r.content))
        zip_file.extractall(self.LOCAL_FOLDER)
        return 

    def parse_file(self):
        # encoding & parsing LOCAL_FILE_NAME
        with codecs.open(self.LOCAL_FILE_NAME, encoding="cp1251") as file:
            data = xmltodict.parse(file.read()) 
        return data
    
    def process(data):
        # @TODO: Ivan add your code here
        None
        
data = Converter()
data.unzip_file()
