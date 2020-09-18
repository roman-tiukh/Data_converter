from __future__ import absolute_import, unicode_literals
from celery import shared_task

from location_register.converter.ratu import RatuDownloader
from location_register.converter.koatuu import KoatuuDownloader
from location_register.converter.drv import DrvUpdater


@shared_task
def update_ratu():
    print('**********************')
    print('*    Update RATU     *')
    print('**********************')

    RatuDownloader().update()

    print('*** Task update_ratu is done. ***')


@shared_task
def update_koatuu():
    print('***********************')
    print('*    Update KOATUU    *')
    print('***********************')

    KoatuuDownloader().update()

    print('*** Task update_koatuu is done. ***')


@shared_task
def update_drv():
    print('********************')
    print('*    Update DRV    *')
    print('********************')

    DrvUpdater().update()

    print('*** Task update_drv is done. ***')



# from __future__ import absolute_import, unicode_literals
#
# import json
# from django.conf import settings
# from celery import shared_task
# from location_register.converter.ratu import RatuConverter
# from location_register.converter.koatuu import KoatuuConverter
# from business_register.converter.kved import KvedConverter

# LOCAL_FILE_KOATUU = settings.LOCATION_KOATUU_LOCAL_FILE_NAME
# LOCAL_FILE_KVED = settings.LOCATION_KVED_LOCAL_FILE_NAME

#
# @shared_task
# def fill_in_ratu_table():
#     RatuConverter().process()
#
#
# @shared_task
# def fill_in_koatuu_table():
#     with open(LOCAL_FILE_KOATUU) as json_file:
#         data = json.load(json_file)
#     KoatuuConverter().save_to_db(data)
#
#
# @shared_task
# def fill_in_kved_table():
#     with open(LOCAL_FILE_KVED) as json_file:
#         data = json.load(json_file)
#     KvedConverter().save_to_db(data)
