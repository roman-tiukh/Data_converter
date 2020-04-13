import codecs
import io
import requests
import sys
import time
from xml.etree.ElementTree import iterparse, XMLParser, tostring
import xmltodict
import zipfile

class Converter:

    FILE_URL=None
    LOCAL_FOLDER=None
    LOCAL_FILE_NAME=None
    
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
            print('Old data have deleted.')

    def process(self):
        # parsing sours file in flow
        # get an iterable
        context = iterparse(self.LOCAL_FOLDER + self.LOCAL_FILE_NAME, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.__next__()

        #clear old DB
        self.clear_db()
        a=0
        b=0
        i=0
        parsing_time=time.time()
        saving_time=time.time()
        record=self.record
        #loop for creating one record
        for event, elem in context:
            if event == "end" and elem.tag == "RECORD":
                for text in elem.iter():
                    print('\t\t', text.tag, '\t\t', text.text)
                    if type(record[text.tag]) == list: 
                        record[text.tag].append(text.text)
                    else:
                        record[text.tag]=text.text
                parsing_time=time.time()
                a=round((parsing_time-saving_time)*1000)
                print('_________________________________')
                print('Processing time, \tms\nparsing \t\t', a)
                
                #writing one record
                self.save_to_db(record, parsing_time)
                
                saving_time=time.time()
                b=round((saving_time-parsing_time)*1000)
                print('total saving \t\t', b)
                print('total processing \t', a+b)
                i=i+1
                print(i, ' records\n\n................................................................................................')
                for key in record:
                    if type(record[key]) == list:
                        record[key].clear()
                    else:
                        record[key]=''
                root.clear()
        print('All the records have been rewritten.')

    print('Converter has imported.')