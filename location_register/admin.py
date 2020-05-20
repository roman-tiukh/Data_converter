from django.contrib import admin

from location_register.models import Region, District, City, Citydistrict, Street

admin.site.register(Region)
admin.site.register(District)
admin.site.register(City)
admin.site.register(Citydistrict)
admin.site.register(Street)
