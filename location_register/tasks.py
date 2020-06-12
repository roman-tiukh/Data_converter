from __future__ import absolute_import, unicode_literals

import json
from django.conf import settings
from celery import shared_task
from location_register.converter.ratu import RatuConverter
from location_register.converter.koatuu import KoatuuConverter

LOCAL_FILE_NAME = settings.LOCATION_KOATUU_LOCAL_FILE_NAME

@shared_task
def fill_in_ratu_table():
    RatuConverter().process()

@shared_task
def fill_in_koatuu_table():
    with open(LOCAL_FILE_NAME) as json_file:
        data = json.load(json_file)
    KoatuuConverter().save_to_db(data)
