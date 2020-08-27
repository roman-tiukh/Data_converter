import os
from datetime import datetime
# import zipfile
import requests
from requests.auth import HTTPBasicAuth
from abc import ABC
# import logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
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
        start_time = datetime.now()
        time_stamp = f'{start_time.date()}_{start_time.hour:02}-{start_time.minute:02}'

        # Create db record & set status "started"
        file_path = f'{self.local_path}{self.reg_name}_{time_stamp}'

        try:
            with requests.get(self.url, data=self.data, stream=self.stream,
                              auth=self.auth, headers=self.get_headers()) as r:
                r.raise_for_status()

                file_size = int(r.headers['Content-Length'])
                print(f'File size: {file_size}.')
                # find last update in db, check prev file length

                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=self.chunk_size):
                        f.write(chunk)

                if os.path.getsize(file_path) != file_size:
                    print(f'File {file_path} is not downloaded! Bad file size.')
                    return

                print(f'File {file_path} is successfully downloaded at {datetime.now() - start_time}.')
                # Create db record & set status "started"set status "downloaded" to db record

                # if self.unzip_after_download:
                #     self.unzip(file_path)

                return file_path

        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)

        # save err to db


class PepDownloader(Downloader):
    url = settings.BUSINESS_PEP_SOURCE_URL
    auth = HTTPBasicAuth(settings.BUSINESS_PEP_AUTH_USER, settings.BUSINESS_PEP_AUTH_PASSWORD)
    chunk_size = 16 * 1024 * 1024
    reg_name = 'pep'


class FopDownloader(Downloader):
    pass


if __name__ == '__main__':
    pass

