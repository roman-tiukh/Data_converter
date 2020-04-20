from django.contrib import admin
from ratu.models.rfop_models import Rfop
from ratu.models.ratu_models import Region,District,City,Citydistrict,Street

admin.site.register(Rfop)
admin.site.register(Region)
admin.site.register(District)
admin.site.register(City)
admin.site.register(Citydistrict)
admin.site.register(Street)

