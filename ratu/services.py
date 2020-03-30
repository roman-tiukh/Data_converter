import codecs
import io
from ratu.models.ratu_models import Region, District, City, Citydistrict, Street
import requests
import sys
import xmltodict
import zipfile
import xml.etree.ElementTree
from xml.etree.ElementTree import iterparse, XMLParser, tostring

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
    
    def clear_db(self):
        # clearing data base
        for table in self.tables:
            table.objects.all().delete()

    def process(self):
        print('4')
        i=0
        record=self.record
        # get an iterable
        context = iterparse(self.LOCAL_FOLDER + self.LOCAL_FILE_NAME, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.__next__()

        self.clear_db()

        for event, elem in context:
            if event == "end" and elem.tag == "RECORD":
                i=i+1
                print(i, '\n\n................................................................................................')
                for text in elem.iter():
                    print(text.tag, text.text)
                    record[text.tag].append(text.text)
                
                self.save_to_db(record)
                
                for key in record:
                    record[key].clear()
                root.clear()

                
    # def process(self): #writing .xml data to db

    #     print('4')

    #     data=self.parse_file()
    #     self.clear_db()
    #     self.save_to_db(data)
        
    # -------------- end of process()