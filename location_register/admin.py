from django.contrib import admin

from location_register.models.ratu_models import RatuRegion, RatuDistrict, RatuCity, RatuCityDistrict, RatuStreet

admin.site.register(RatuRegion)
admin.site.register(RatuDistrict)
admin.site.register(RatuCity)
admin.site.register(RatuCityDistrict)
admin.site.register(RatuStreet)
