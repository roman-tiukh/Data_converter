from data_ocean.converter import Converter
from location_register.models.address_models import Country


class AddressConverter(Converter):

    def __init__(self):
        self.all_countries_dict = self.put_objects_to_dict("name", "location_register", "Country")
        super().__init__()

    def save_or_get_country(self, name):
        name = name.lower()
        if name not in self.all_countries_dict:
            new_country = Country.objects.create(name=name)
            self.all_countries_dict[name] = new_country
            return new_country
        return self.all_countries_dict[name]
