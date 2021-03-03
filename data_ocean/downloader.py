import logging
import os
import subprocess
import zipfile
from abc import ABC

import requests
from django.apps import apps
from django.conf import settings
from django.db import connections
from django.utils import timezone

from data_ocean.models import RegistryUpdaterModel, Register
from business_register.models.company_models import Company

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

    def is_zip_file(self):
        if not zipfile.is_zipfile(self.file_path):
            msg = f'Error! {self.file_path} is not a Zip file!'
            self.log_obj.unzip_message = msg
            self.log_obj.save()
            logger.exception(f'{self.reg_name}: {msg}')
            raise Exception('Unzip error!', msg)
        return True

    def test_zip_file(self):
        logger.info(f'{self.reg_name}: Test archive {self.file_path} start...')
        test_error = subprocess.run(['unzip', '-t', self.file_path]).returncode
        if test_error:
            msg = f'Error! Test archive {self.file_path} failed!'
            self.log_obj.unzip_message = msg
            self.log_obj.save()
            logger.exception(f'{self.reg_name}: {msg}')
            raise Exception('Unzip error!', msg)
        logger.info(f'{self.reg_name}: Test archive finished successfully.')
        return True

    def get_zip_filelist(self):
        file_list = zipfile.ZipFile(self.file_path).namelist()
        logger.info(f'{self.reg_name}: Archive file list: {file_list}')
        return file_list

    def unzip_result(self, i):
        logger.info(f'{self.reg_name}: Unzipping {self.file_path} ...')
        unzip_status = subprocess.run(['unzip', '-o', self.file_path, i, '-d', self.local_path]).returncode
        if not unzip_status:
            logger.info(f'{self.reg_name}: Unzipping {self.file_path} finished successfully.')
            self.remove_file()
            self.file_name = i
            self.file_path = self.local_path + self.file_name
            self.log_obj.unzip_file_name = self.file_name
            self.log_obj.unzip_status = True
            self.log_obj.save()
            return True

        msg = f'Error! Unzip failed for {self.file_path}! Return status: {unzip_status}!'
        self.log_obj.unzip_message = msg
        self.log_obj.save()
        logger.exception(f'{self.reg_name}: {msg}')
        raise Exception('Error!', msg)

    def no_req_sign(self):
        msg = f'Error! Unzip failed for {self.file_path}! File with required sign not found!'
        self.log_obj.unzip_message = msg
        self.log_obj.save()
        logger.exception(f'{self.reg_name}: {msg}')
        raise Exception('Error!', msg)

    def unzip_source_file(self):
        self.is_zip_file()
        self.test_zip_file()
        for i in self.get_zip_filelist():
            if self.unzip_required_file_sign in i:
                if self.unzip_result(i):
                    return
        self.no_req_sign()

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

                logger.info(
                    f"{self.reg_name}: {self.file_path} downloaded successfully at {timezone.now() - start_time}.")

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
            raise Exception('Error!', e)

        if self.unzip_after_download:
            self.unzip_source_file()

    def update_register_field(self, register_api_list, field_name, new_field_value):
        register = Register.objects.get(api_list=register_api_list)
        setattr(register, field_name, new_field_value)
        register.save(update_fields=[field_name, 'updated_at'])

    def measure_changes(self, app_name, model_name):
        model = apps.get_model(app_name, model_name)
        self.log_obj.records_added = model.objects.filter(
            created_at__range=[self.log_obj.update_start, self.log_obj.update_finish]
        ).count()
        self.log_obj.records_changed = model.objects.filter(
            updated_at__range=[self.log_obj.update_start, self.log_obj.update_finish]
        ).count()
        self.log_obj.records_deleted = model.objects.filter(
            deleted_at__range=[self.log_obj.update_start, self.log_obj.update_finish]
        ).count()
        self.log_obj.save()

    def measure_company_changes(self, source):
        self.log_obj.records_added = Company.objects.filter(
            source=source,
            created_at__range=[self.log_obj.update_start, self.log_obj.update_finish]
        ).count()
        self.log_obj.records_changed = Company.objects.filter(
            source=source,
            updated_at__range=[self.log_obj.update_start, self.log_obj.update_finish]
        ).count()
        self.log_obj.records_deleted = Company.objects.filter(
            source=source,
            deleted_at__range=[self.log_obj.update_start, self.log_obj.update_finish]
        ).count()
        self.log_obj.save()



