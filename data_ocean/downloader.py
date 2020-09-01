import os
from django.utils import timezone
# import zipfile
import requests
# from requests.auth import HTTPBasicAuth
from abc import ABC
# import logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
from data_ocean.models import RegistryUpdaterModel
from django.conf import settings


class Downloader(ABC):
    auth = None
    url = None
    unzip_after_download = False
    data = {}
    headers = {}
    check_by_length = False
    local_path = settings.LOCAL_FOLDER
    chunk_size = 8 * 1024 * 1024
    stream = True
    reg_name = ''

    def __init__(self):
        assert self.url
        assert self.reg_name
        assert self.local_path

    def get_headers(self):
        return self.headers

    def unzip(self, file):
        pass

    def remove_downloaded_file(self, file_path):
        if os.path.isfile(file_path):
            os.remove(file_path)

    def download(self):
        start_time = timezone.now()
        time_stamp = f'{start_time.date()}_{start_time.hour:02}-{start_time.minute:02}'
        file_path = f'{self.local_path}{self.reg_name}_{time_stamp}'

        upd_obj = RegistryUpdaterModel.objects.create(registry_name=self.reg_name)
        if not upd_obj:
            print(f"Can't create log record in db!")
            return None, None

        try:
            with requests.get(self.url, data=self.data, stream=self.stream,
                              auth=self.auth, headers=self.get_headers()) as r:
                r.raise_for_status()

                file_size = int(r.headers['Content-Length'])
                print(f'File size: {file_size}.')

                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=self.chunk_size):
                        f.write(chunk)
                    f.flush()

                if os.path.getsize(file_path) != file_size:
                    upd_obj.download_finish = timezone.now()
                    upd_obj.download_message = 'Download Error: Bad file size after download.'
                    upd_obj.save()
                    self.remove_downloaded_file(file_path)
                    print(f'File {file_path} is not downloaded! Bad file size after download.')
                    return None, None

                upd_obj.download_finish = timezone.now()
                upd_obj.download_status = True
                upd_obj.download_file_name = file_path
                upd_obj.download_file_length = file_size
                upd_obj.save()
                print(f'File {file_path} is successfully downloaded at {timezone.now() - start_time}.')

                # if self.unzip_after_download:
                #     self.unzip(file_path)

                return file_path, upd_obj.id

        except requests.exceptions.HTTPError as errh:
            upd_obj.download_message = f'Http Error: {errh}'[255:]
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            upd_obj.download_message = f'Connecting Error: {errc}'[255:]
            print("Connecting Error:", errc)
        except requests.exceptions.Timeout as errt:
            upd_obj.download_message = f'Http Error: {errt}'[255:]
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            upd_obj.download_message = f'Error: {err}'[255:]
            print("Error:", err)
        upd_obj.download_finish = timezone.now()
        upd_obj.save()
        return None, None
