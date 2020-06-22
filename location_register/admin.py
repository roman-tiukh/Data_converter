from django.contrib import admin

from location_register.models.ratu_models import Region, District, City, CityDistrict, Street

admin.site.register(Region)
admin.site.register(District)
admin.site.register(City)
admin.site.register(CityDistrict)
admin.site.register(Street)
