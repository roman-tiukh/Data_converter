import os

import requests
import urllib3
import xlrd
from django.conf import settings
from django.core.management import BaseCommand

from business_register.models.declaration_models import LuxuryCar


class Command(BaseCommand):
    help = 'Saving a list of cars that are subject to transport tax'

    def __init__(self, *args, **kwargs):
        self.LOCAL_FILE_NAME = 'luxury_car.xlsx'
        self.LOCAL_PATH = settings.LOCAL_FOLDER + self.LOCAL_FILE_NAME
        self.URL = settings.LUXURY_CAR_URL
        self.FILE_ID = settings.FILE_ID_DICT
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        FUEL_TYPES = {
            'бензин': LuxuryCar.PETROL,
            'дизель': LuxuryCar.DIESEL,
            'гібрид': LuxuryCar.HYBRID,
            'бензин, електро': LuxuryCar.PETROL_ELECTRIC,
            'гібрид (бензин, електро)': LuxuryCar.PETROL_ELECTRIC,
            'дизель, електро': LuxuryCar.DIESEL_ELECTRIC,
            'бензин (гібрид)': LuxuryCar.HYBRID,
            'електро': LuxuryCar.ELECTRIC,
        }
        for year in self.FILE_ID:
            current_year = LuxuryCar.objects.filter(document_year=year).first()
            if current_year:
                continue
            else:
                all_car = []
                urllib3.disable_warnings()
                with requests.get(self.URL + self.FILE_ID[year], verify=False) as r:
                    with open(self.LOCAL_PATH, 'wb') as path:
                        path.write(r.content)
                rb = xlrd.open_workbook(self.LOCAL_PATH, formatting_info=True)
                sheet = rb.sheet_by_index(0)
                norm_sheet = []
                for row in range(0, sheet.nrows):
                    if sheet.row_values(row)[0]:
                        norm_sheet.append(sheet.row_values(row))
                for row in norm_sheet[2:]:
                    brand = row[0].strip().lower()
                    model = str(row[1]).strip().lower()
                    current_car = [brand, model]
                    if current_car not in all_car:
                        doc_year = year
                        after_year = int(year) - int(row[2].split(' ')[1])
                        volume = float(row[3]) if row[3] and row[3] != 'н/д' and int(row[3]) < 10 else None
                        fuel = FUEL_TYPES.get(row[4].lower().strip()) if row[4] else None
                        if row[4] and not fuel:
                            self.stdout.write(f'New type of fuel {row[4]}')
                        LuxuryCar.objects.create(
                            brand=brand,
                            model=model,
                            after_year=after_year,
                            document_year=doc_year,
                            volume=volume,
                            fuel=fuel,
                        )
                        all_car.append(current_car)
                        # TODO explore whether it is possible to normalize data from the 5th column
                    else:
                        continue
                os.remove(f'{self.LOCAL_PATH}')
