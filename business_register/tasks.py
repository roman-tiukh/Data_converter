from __future__ import absolute_import, unicode_literals
from celery import shared_task

from business_register.converter.pep import PepConverter
from data_ocean.downloader import PepDownloader


@shared_task
def update_pep():
    print('********************')
    print('*    Update PEP    *')
    print('********************')

    file_path = PepDownloader().download()
    if file_path:
        print(f'file_path = {file_path}')
        PepConverter().save_to_db(file_path)
        PepDownloader().remove_downloaded_file(file_path)

    print('*** Task update_pep is done. ***')
