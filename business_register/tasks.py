from __future__ import absolute_import, unicode_literals
from celery import shared_task

from business_register.converter.pep import PepConverter, PepDownloader


@shared_task
def update_pep():
    print('********************')
    print('*    Update PEP    *')
    print('********************')

    file_path, log_id = PepDownloader().download()
    if file_path and log_id:
        PepConverter().save_to_db(file_path, log_id)
        PepDownloader().remove_downloaded_file(file_path)

    print('*** Task update_pep is done. ***')
