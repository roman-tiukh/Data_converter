from django.core.management import BaseCommand

from business_register.converter.declaration import DeclarationConverter
from business_register.models.declaration_models import Vehicle


class Command(BaseCommand):
    help = '---'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.converter = DeclarationConverter()

    def add_arguments(self, parser):
        parser.add_argument('--declaration_nacp_id', nargs='?', type=str)
        parser.add_argument('--pep_id', nargs='?', type=int)

    def is_luxury_cars(self, cars):
        i = 0
        count = cars.count()
        for car in cars:
            i += 1
            self.stdout.write(f'\rProgress: {i} of {count}', ending='')
            self.stdout.flush()
            self.converter.current_declaration = car.declaration
            car.is_luxury = self.converter.is_vehicle_luxury(car)
            car.save()
        self.stdout.write()
        self.stdout.write('Done!')

    def handle(self, *args, **options):
        declaration_nacp_id = options['declaration_nacp_id']
        pep_id = options['pep_id']
        if pep_id:
            cars = Vehicle.objects.filter(type=Vehicle.CAR, declaration__pep_id=pep_id)
            self.is_luxury_cars(cars)
        elif declaration_nacp_id:
            cars = Vehicle.objects.filter(
                type=Vehicle.CAR,
                declaration__nacp_declaration_id=declaration_nacp_id,
            )
            self.is_luxury_cars(cars)
        else:
            all_cars = Vehicle.objects.filter(type=Vehicle.CAR)
            self.is_luxury_cars(all_cars)
