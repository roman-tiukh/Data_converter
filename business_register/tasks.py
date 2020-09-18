from __future__ import absolute_import, unicode_literals
from celery import shared_task

from business_register.converter.pep import PepDownloader
from business_register.converter.fop import FopDownloader
from business_register.converter.kved import KvedDownloader


@shared_task
def update_pep():
    print('********************')
    print('*    Update PEP    *')
    print('********************')

    PepDownloader().update()

    print('*** Task update_pep is done. ***')


@shared_task
def update_fop():
    print('********************')
    print('*    Update FOP    *')
    print('********************')

    FopDownloader().update()

    print('*** Task update_fop is done. ***')


@shared_task
def update_kved():
    print('*********************')
    print('*    Update KVED    *')
    print('*********************')

    KvedDownloader().update()

    print('*** Task update_kved is done. ***')
