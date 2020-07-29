import codecs
import json
import os
import zipfile
from collections import defaultdict
from xml.etree.ElementTree import iterparse

import requests
import xmltodict
from django.apps import apps
from lxml import etree


class Converter:
    UPDATE_FILE_NAME = "update.cfg"
    API_ADDRESS_FOR_DATASET = ""  # specified api address with dataset id
    LOCAL_FILE_NAME = None  # static short local filename
    LOCAL_FOLDER = "source_data/"  # local folder for unzipped source files
    DOWNLOAD_FOLDER = "download/"  # folder to downloaded files
    URLS_DICT = {}  # control remote dataset files update

    def load_json(self, json_file):
        with open(json_file) as file:
            return json.load(file)

    # lets have all supporting functions at the beginning
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

    def process_full(self):  # It's temporary method name, in the future this 'process' will be one
        i = 0
        records = etree.Element('RECORDS')
        for _, elem in etree.iterparse(self.LOCAL_FOLDER + self.LOCAL_FILE_NAME, tag=self.RECORD_TAG):
            if len(records) < self.CHUNK_SIZE:
                # for text in elem.iter():
                #     print('\t%28s\t%s' % (text.tag, text.text))
                records.append(elem)
                i = i + 1
                print(i,
                      'record\n\n................................................................................................')
            else:
                self.save_to_db(records)
                records.clear()
        print('All the records have been rewritten.')

    print('Converter has imported.')


class BulkCreateManager(object):  # https://www.caktusgroup.com/blog/2019/01/09/django-bulk-inserts/
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size):
        self.create_queues = defaultdict(list)
        self.stored_objects = defaultdict(list)
        self.chunk_size = chunk_size

    def commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self.create_queues[model_key])
        for stored_object in self.create_queues[model_key]:
            self.stored_objects[model_key].append(stored_object)
        self.create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self.create_queues[model_key].append(obj)
        if len(self.create_queues[model_key]) >= self.chunk_size:
            self.commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self.create_queues.items():
            if len(objs) > 0:
                self.commit(apps.get_model(model_name))
