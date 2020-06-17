from __future__ import absolute_import, unicode_literals

import json
from django.conf import settings
from celery import shared_task
from location_register.converter.ratu import RatuConverter
from location_register.converter.koatuu import KoatuuConverter
from business_register.converter.kved import KvedConverter

LOCAL_FILE_KOATUU = settings.LOCATION_KOATUU_LOCAL_FILE_NAME
LOCAL_FILE_KVED = settings.LOCATION_KVED_LOCAL_FILE_NAME

@shared_task
def fill_in_ratu_table():
    RatuConverter().process()

@shared_task
def fill_in_koatuu_region_and_district_table():
    with open(LOCAL_FILE_KOATUU) as json_file:
        data = json.load(json_file)
    KoatuuConverter().save_to_db_region_and_district(data)
    KoatuuConverter().save_to_db_city_and_citydistrict(data)

@shared_task
def fill_in_kved_table():
    with open(LOCAL_FILE_KVED) as json_file:
        data = json.load(json_file)
    KvedConverter().save_to_db(data)

# @shared_task
# def task_one():
#     print('Hello ')

# @shared_task
# def task_two():
#     print(' my friend!!')
