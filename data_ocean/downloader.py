import os
import subprocess
from django.utils import timezone
import zipfile
import requests
from abc import ABC
import logging
from django.db import connections
import timeit
from datetime import datetime
# import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from data_ocean.models import RegistryUpdaterModel
from django.conf import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Downloader(ABC):
    auth = None
    url = None
    data = {}
    headers = {}
    local_path = settings.LOCAL_FOLDER
    chunk_size = 8 * 1024 * 1024
    stream = True
    reg_name = ''
    file_name = ''
    file_path = ''
    file_size = 0
    check_by_length = False
    zip_required_file_sign = ''
    unzip_required_file_sign = ''
    unzip_after_download = False
    log_obj = None
    start_time = None
    source_dataset_url = ''

    def __init__(self):
        assert self.reg_name
        assert self.local_path
        self.url = self.get_source_file_url()
        assert self.url
        self.file_name = self.get_source_file_name()
        assert self.file_name
        self.file_path = self.local_path + self.file_name

    def get_headers(self):
        return self.headers

    def unzip_file(self):
        if not zipfile.is_zipfile(self.file_path):
            msg = f'Error! {self.file_path} is not a Zip file!'
            self.log_obj.unzip_message = msg
            self.log_obj.save()
            logger.exception(f'{self.reg_name}: {msg}')
            exit(1)

        logger.info(f'{self.reg_name}: Test archive {self.file_path} start...')
        test_error = subprocess.run(['unzip', '-t', self.file_path]).returncode
        if test_error:
            msg = f'Error! Test archive {self.file_path} failed!'
            self.log_obj.unzip_message = msg
            self.log_obj.save()
            logger.exception(f'{self.reg_name}: {msg}')
            exit(1)
        logger.info(f'{self.reg_name}: Test archive finished successfully.')

        file_list = zipfile.ZipFile(self.file_path).namelist()
        logger.info(f'{self.reg_name}: Archive file list: {file_list}')
        for i in file_list:
            if self.unzip_required_file_sign in i:
                logger.info(f'{self.reg_name}: Unzipping {self.file_path} ...')
                unzip_status = subprocess.run(['unzip', '-o', self.file_path, i, '-d', self.local_path]).returncode
                if not unzip_status:
                    logger.info(f'{self.reg_name}: Unzipping {self.file_path} finished successfully.')
                    self.file_name = i
                    self.file_path = self.local_path + self.file_name
                    self.log_obj.unzip_file_name = self.file_name
                    self.log_obj.unzip_status = True
                    self.log_obj.save()
                    return

        msg = f'Error! Unzip failed for {self.file_path}! File with required sign not found!'
        self.log_obj.unzip_message = msg
        self.log_obj.save()
        logger.exception(f'{self.reg_name}: {msg}')
        exit(1)

    def file_size_is_correct(self):
        if os.path.isfile(self.file_path):
            return os.path.getsize(self.file_path) == self.file_size

    def remove_file(self):
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)

    def log_init(self):
        self.log_obj = RegistryUpdaterModel.objects.create(registry_name=self.reg_name)

    def get_source_file_url(self):
        assert self.url
        return self.url

    def get_source_file_name(self):
        assert self.file_name
        return self.file_name

    def vacuum_analyze(self, table_list=None):
        query = 'select count(*) from'
        query_optimize = 'vacuum analyze'

        with connections['default'].cursor() as c:
            for table in table_list:
                start_time = timezone.now()
                c.execute('%s %s' % (query_optimize, table))
                logger.info(f'{self.reg_name}: {query_optimize} {table} at {timezone.now() - start_time}')
                start_time = timezone.now()
                c.execute('%s %s' % (query, table))
                logger.info(f'{self.reg_name}: {query} {table} at {timezone.now() - start_time}')

    def download(self):
        assert self.url
        assert self.file_path

        start_time = timezone.now()
        try:
            with requests.get(self.url, data=self.data, stream=self.stream,
                              auth=self.auth, headers=self.get_headers()) as r:
                r.raise_for_status()

                self.file_size = int(r.headers['Content-Length'])
                logger.info(f"{self.reg_name}: Start downloading: {self.file_path}, size: {self.file_size} ...")
                self.remove_file()
                with open(self.file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=self.chunk_size):
                        f.write(chunk)
                    f.flush()

                if not self.file_size_is_correct():
                    raise requests.exceptions.RequestException('Error! Bad file size after download.')

                logger.info(f"{self.reg_name}: {self.file_path} downloaded successfully at {timezone.now() - start_time}.")

                self.log_obj.download_finish = timezone.now()
                self.log_obj.download_status = True
                self.log_obj.download_file_name = self.file_path
                self.log_obj.download_file_length = self.file_size
                self.log_obj.save()

        except requests.exceptions.RequestException as e:

            self.log_obj.download_finish = timezone.now()
            self.log_obj.download_status = False
            self.log_obj.download_message = f'{e}'[:255]
            self.log_obj.save()
            logger.exception(f'{self.reg_name}: {e}')
            exit(1)

        if self.unzip_after_download:
            self.unzip_file()
