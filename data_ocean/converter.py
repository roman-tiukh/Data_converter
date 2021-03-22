import codecs
import json
import logging
import os
import traceback
import zipfile
from collections import defaultdict

import requests
import xmltodict
from django.apps import apps
from lxml import etree

from location_register.models.address_models import Country

logger = logging.getLogger(__name__)


class Converter:
    UPDATE_FILE_NAME = "update.cfg"
    API_ADDRESS_FOR_DATASET = ""  # specified api address with dataset id
    LOCAL_FILE_NAME = None  # static short local filename
    LOCAL_FOLDER = "source_data/"  # local folder for unzipped source files
    DOWNLOAD_FOLDER = "download/"  # folder to downloaded files
    URLS_DICT = {}  # control remote dataset files update

    def __init__(self):
        self.all_countries_dict = self.put_objects_to_dict("name", "location_register", "Country")

    def save_or_get_country(self, name):
        name = name.lower()
        if name not in self.all_countries_dict:
            new_country = Country.objects.create(name=name)
            self.all_countries_dict[name] = new_country
            return new_country
        return self.all_countries_dict[name]

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

    def put_objects_to_dict(self, key_field, app_name, model_name):
        return {getattr(obj, key_field): obj for obj in apps.get_model(
            app_name,
            model_name
        ).objects.all()
                }

    def put_objects_to_dict_with_two_fields_key(self, first_field, second_field, app_name, model_name):
        return {f'{getattr(obj, first_field)}_{getattr(obj, second_field)}':
                    obj for obj in apps.get_model(
            app_name,
            model_name
        ).objects.all()
                }

    def delete_outdated(self):
        """ delete some outdated records """

    def process(self, start_index=0):
        records = []
        elements = etree.iterparse(
            source=self.LOCAL_FOLDER + self.LOCAL_FILE_NAME,
            tag=self.RECORD_TAG,
            recover=False,
        )

        # for _ in range(start_index):
        #     next(elements)

        # i = start_index
        i = 0
        chunk_start_index = i
        for _, elem in elements:
            records_len = len(records)

            if records_len == 0:
                chunk_start_index = i

            # for text in elem.iter():
            #     print('\t%28s\t%s' % (text.tag, text.text))

            records.append(elem)
            records_len += 1
            if records_len >= self.CHUNK_SIZE:
                # print(f'>>> Start save to db records {chunk_start_index}-{i}')
                try:
                    if i >= start_index:
                        self.save_to_db(records)
                    print(i)
                except Exception as e:
                    msg = f'!!! Save to db failed at index = {chunk_start_index}. Error: {str(e)}'
                    logger.error(msg)
                    traceback.print_exc()
                    print(msg)
                    raise Exception('Error!', msg)
                records.clear()

                # http://lxml.de/parsing.html#modifying-the-tree
                # Based on Liza Daly fast_iter
                # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
                # See also http://effbot.org/zone/element-iterparse.htm
                #
                # It safe to call clear() here because no descendants will be accessed
                elem.clear()
                # # Also eliminate now-empty references from the root node to elem
                for ancestor in elem.xpath('ancestor-or-self::*'):
                    while ancestor.getprevious() is not None:
                        del ancestor.getparent()[0]

                print('>>> Saved successfully')
            i += 1
        if records_len:
            self.save_to_db(records)
        if start_index == 0:
            self.delete_outdated()
        del elements
        print('All the records have been rewritten.')

    print('Converter has imported.')


class BulkCreateManager(object):  # https://www.caktusgroup.com/blog/2019/01/09/django-bulk-inserts/
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes.
    The developer must clear all queues after all objects are created for all models.
    """

    def __init__(self):
        self.queues = defaultdict(list)

    def commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self.queues[model_key])

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self.queues[model_key].append(obj)
