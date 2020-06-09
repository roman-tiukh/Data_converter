import codecs
from collections import defaultdict
from django.apps import apps
import datetime
import json
import io
from lxml import etree
import os
import requests
import sys
from xml.etree.ElementTree import iterparse, XMLParser, tostring
import xmltodict
import zipfile

from business_register.models.kved_models import Kved
from data_ocean.models import Status, Authority, TaxpayerType

class Converter:
    UPDATE_FILE_NAME = "update.cfg"
    API_ADDRESS_FOR_DATASET = ""  # specified api address with dataset id
    LOCAL_FILE_NAME = None  # static short local filename
    LOCAL_FOLDER = "source_data/"  # local folder for unzipped source files
    DOWNLOAD_FOLDER = "download/"  # folder to downloaded files
    URLS_DICT = {}  # control remote dataset files update
    #dictionaries whith all kveds, statuses, authorities and taxpayer_types
    all_kveds_dict = {}  
    all_statuses_dict = {}
    all_authorities_dict = {}
    all_taxpayer_types_dict = {}

    # initializing dictionaries with all objects
    def __init__(self):
        self.all_kveds_dict = self.put_all_objects_to_dict_with_code("business_register", "Kved")
        self.all_statuses_dict = self.put_all_objects_to_dict_with_name("data_ocean", "Status")
        self.all_authorities_dict = self.put_all_objects_to_dict_with_name("data_ocean", "Authority")
        self.all_taxpayer_types_dict = self.put_all_objects_to_dict_with_name("data_ocean", "TaxpayerType")

    # putting all objects of the model from DB to a dictionary using name as a key
    def put_all_objects_to_dict_with_name(self, app_name, model_name):
        model = apps.get_model(app_name, model_name)
        all_objects = model.objects.all()
        all_objects_dict = {}
        for object in all_objects:
            all_objects_dict[object.name] = object
        return all_objects_dict
    
    # putting all objects of the model from DB to a dictionary using code as a key
    def put_all_objects_to_dict_with_code(self, app_name, model_name):
        model = apps.get_model(app_name, model_name)
        all_objects = model.objects.all()
        all_objects_dict = {}
        for object in all_objects:
            all_objects_dict[object.code]=object
        return all_objects_dict

    # putting objects of the model from DB to a dictionary using region as a filter
    def put_objects_from_region_to_dict(self, app_name, model_name, region_name):
        model = apps.get_model(app_name, model_name)
        region_objects = model.objects.filter(region=region_name)
        region_objects_dict = {}
        for object in region_objects:
            region_objects_dict[object.name]=object
        return region_objects_dict

    #lets have all supporting functions at the beginning
    def get_first_word(self, string):
        return string.split()[0]

    def cut_first_word(self, string):
        words_after_first = string.split()[1:]
        return " ".join(words_after_first)

    def format_date_to_yymmdd(self, str_ddmmyy): 
        ddmmyy = str_ddmmyy.replace(";", "")
        return datetime.datetime.strptime(ddmmyy, "%d.%m.%Y").strftime("%Y-%m-%d")
        
    #verifying kved
    def get_kved_from_DB(self, kved_code_from_record):
        empty_kved = Kved.objects.get(code='EMP')
        if kved_code_from_record in self.all_kveds_dict:
            return self.all_kveds_dict[kved_code_from_record]
        print(f"This kved value is outdated or not valid")
        return empty_kved
    
    def save_or_get_status(self, status_from_record):
        #storing an object that isn`t in DB yet
        if not status_from_record in self.all_statuses_dict:
            new_status = Status(name=status_from_record)
            new_status.save()
            self.all_statuses_dict[status_from_record] = new_status
            return new_status
        #getting an existed object from DB
        return self.all_statuses_dict[status_from_record]

    def save_or_get_authority(self, authority_from_record):
        #storing an object that isn`t in DB yet
        if not authority_from_record in self.all_authorities_dict:
            new_authority = Authority(name=authority_from_record)
            new_authority.save()
            self.all_authorities_dict[authority_from_record] = new_authority
            return new_authority
        #getting an existed object from DB
        return self.all_authorities_dict[authority_from_record]

    def save_or_get_taxpayer_type(self, taxpayer_type_from_record):
        #storing an object that isn`t in DB yet
        if not taxpayer_type_from_record in self.all_taxpayer_types_dict:
            new_taxpayer_type = TaxpayerType(name=taxpayer_type_from_record)
            new_taxpayer_type.save()
            self.all_taxpayer_types_dict[taxpayer_type_from_record] = new_taxpayer_type
            return new_taxpayer_type
        #getting an existed object from DB
        return self.all_taxpayer_types_dict[taxpayer_type_from_record]

    def get_urls(self):
        # returns actual dataset urls
        response = requests.get(self.API_ADDRESS_FOR_DATASET)
        if (response.status_code != 200):
            print(f"ERROR request to {self.API_ADDRESS_FOR_DATASET}")
            return response.status_code
        urls = []
        for i in response.json()['result']['resources']:
            urls.append(i['url'])
        return (urls)

    def rename_file(self, file):
        # abstract method for rename unzipped files for each app
        return

    def is_update(self, current_size, url):
        # returns true, if file size at the <url> changed compared to current_size

        try:
            with open(self.UPDATE_FILE_NAME) as file:
                try:
                    self.URLS_DICT = json.load(file)
                except:
                    pass
        except:
            pass

        if len(self.URLS_DICT) > 0:
            if url in self.URLS_DICT:
                if int(self.URLS_DICT[url]) == current_size:
                    return False

        return True

    def change_update(self, current_size, url):
        # update json, contains url & remote files size

        self.URLS_DICT[url] = current_size
        file = open(self.UPDATE_FILE_NAME, "w")
        file.write(json.dumps(self.URLS_DICT))
        file.close

    def download_file(self):
        # getting remote file from self.file_url
        urls = self.get_urls()
        for url in urls:
            file = os.path.split(url)[1]
            # request to remote url:
            print(f"\nRequest to remote url > {url}")
            response = requests.get(url, stream=True)
            print(f"\tResponse: {response.status_code}")
            if (response.status_code != 200):
                print(f"E\tRROR of requests.get ({url})")
                continue

            # check for remote file updates:
            file_size = int(response.headers['Content-Length'])
            if not (self.is_update(file_size, url)):
                print(f"- File {file} did not update. Not need to download.")
                continue

            # folder existing control:
            if not (os.path.exists(self.DOWNLOAD_FOLDER)) or not (os.path.isdir(self.DOWNLOAD_FOLDER)):
                os.mkdir(self.DOWNLOAD_FOLDER)
            if not (os.path.exists(self.LOCAL_FOLDER)) or not (os.path.isdir(self.LOCAL_FOLDER)):
                os.mkdir(self.LOCAL_FOLDER)

            # download file:
            fd = open(self.DOWNLOAD_FOLDER + file, 'wb')
            print(f"Download file {fd.name} ({'{0:,}'.format(file_size).replace(',', ' ')} bytes total):")
            done = 0
            buffer_size = 1024 * 1024 * 10
            step = 10

            for chunk in response.iter_content(chunk_size=buffer_size):
                fd.write(chunk)
                fd.flush()
                done += buffer_size
                if done > file_size: done = file_size
                percent = round((done / file_size * 100))
                if (percent >= step):
                    if percent > 100: percent = 100
                    print(f"\t{percent} % ===> {'{0:,}'.format(done).replace(',', ' ')} bytes")
                    step += 10

            fd.close()
            if (os.stat(self.DOWNLOAD_FOLDER + file).st_size == file_size):
                print(f"File {file} downloaded succefully.")
                self.change_update(file_size, url)

            else:
                print("Download file error")
                self.delete_downloaded_file(file)
                continue

            if zipfile.is_zipfile(self.DOWNLOAD_FOLDER + file):
                self.unzip_file(self.DOWNLOAD_FOLDER + file)
            else:
                os.rename(self.DOWNLOAD_FOLDER + file, self.LOCAL_FOLDER + self.LOCAL_FILE_NAME)

    def unzip_file(self, file):
        # unzip downloaded file
        print(f"Unzipping file {file} ...")
        try:
            zip_file = zipfile.ZipFile(file)
            zip_file.extractall(self.LOCAL_FOLDER)
            print("\tUnzip succefully.")
        except:
            print(f"\tERROR unzip file {file}")

        # rename & move unzipped files:
        for unzipped_file in zip_file.namelist():
            os.rename(self.LOCAL_FOLDER + unzipped_file, self.LOCAL_FOLDER + self.rename_file(unzipped_file))

        self.delete_downloaded_file(file)

    def delete_downloaded_file(self, file):
        # deleting zipfile:
        try:
            os.remove(file)
        except:
            print(f"ERROR deleting file {file}")

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

        # clear old DB
        self.clear_db()

        i = 0
        record = self.record
        # loop for creating one record
        for event, elem in context:
            if event == "end" and elem.tag == "RECORD":
                for text in elem.iter():
                    print('\t\t', text.tag, '\t\t', text.text)
                    if type(record[text.tag]) == list:
                        record[text.tag].append(text.text)
                    else:
                        record[text.tag] = text.text

                # writing one record
                self.save_to_db(record)

                i = i + 1
                print(i,
                      ' records\n\n................................................................................................')
                for key in record:
                    if type(record[key]) == list:
                        record[key].clear()
                    else:
                        record[key] = ''
                root.clear()
        try:
            self.bulk_manager.done()
        except:
            None
        try:
            self.bulk_submanager.done()
        except:
            None
        print('All the records have been rewritten.')
    
    def process_full(self): # It's temporary method name, in the future this 'process' will be one       
        self.clear_db()
        i = 0
        records = etree.Element('RECORDS')
        for _, elem in etree.iterparse(self.LOCAL_FOLDER + self.LOCAL_FILE_NAME, tag = 'SUBJECT'):           
            if len(records) < self.CHUNK_SIZE:
                for text in elem.iter():
                    print('\t%28s\t%s'%(text.tag, text.text))
                records.append(elem)
                i = i + 1
                print(i,
                    'record\n\n................................................................................................')
            else:
                self.save_to_db(records)
                records.clear()
        print('All the records have been rewritten.')
    print('Converter has imported.')

class BulkCreateUpdateManager(object):  # https://www.caktusgroup.com/blog/2019/01/09/django-bulk-inserts/
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=200):
        self._create_queues = defaultdict(list)
        self._update_queues = defaultdict(list)
        self.chunk_size = chunk_size
        self.create_first = False
        self.update_first = False

    def _commit_create(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self.create_first = True

    def _commit_update(self, model_class, fields):
        model_key = model_class._meta.label
        model_class.objects.bulk_update(self._update_queues[model_key], fields)
        self.update_first = True

    def add_create(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label

        if self.create_first:
            self._create_queues[model_key] = []
            self.create_first = False
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit_create(model_class)

    def add_update(self, obj):
        """
        Add an object to the queue to be updated, and call bulk_update if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label

        if self.update_first:
            self._update_queues[model_key] = []
            self.update_first = False
        self._update_queues[model_key].append(obj)
        if len(self._update_queues[model_key]) >= self.chunk_size:
            self._commit_update(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))