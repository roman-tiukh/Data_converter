import zipfile
import xmltodict
import sys, codecs
#pip3 install service
#pip3 freeze > requirements.txt
from service import Service
import urllib.request

class Converter (Service):
    file_url = "https://data.gov.ua/dataset/75e57837-128b-49e1-a007-5e7dfa7bf6af/resource/e21a1e57-051c-46ea-9c8e-8f30de7d863d/download/"
    file_name = "28-ex_xml_atu.zip"
    local_file = "unzipped_xml/xml.xml"

    def __init__ (self):
        return

    def unzip_file (self):
        remote_file = urllib.request.urlopen(self.file_url + self.file_name)
        if remote_file.getcode() == 200:
            zip = open(self.local_file, "wb")
            zip.write(remote_file)
            zip.close()

            zip = zipfile.ZipFile(self.local_file, "r")
            print (zipfile.is_zipfile(zip))
            # print (file.info())
            # with zipfile.ZipFile(self.file_url + self.file_name, 'r') as zip_ref:
            #     zip_ref.extractall(self.local_file)

    def get_file (self):
        with codecs.open(local_file, encoding="cp1251") as file:
            data = xmltodict.parse(file.read()) 

        print (data['DATA']['RECORD'][5])
        
get_data = Converter()

get_data.unzip_file()
# get_data.get_file()







