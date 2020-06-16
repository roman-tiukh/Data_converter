from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from business_register.models.kved_models import Kved, Group, Division, Section
from business_register.models.rfop_models import Rfop, Fop
from business_register.models.company_models import Company

admin.site.register(Rfop)
admin.site.register(Fop)
admin.site.register(Kved)
admin.site.register(Group)
admin.site.register(Division)
admin.site.register(Section)
admin.site.register(Company, SimpleHistoryAdmin)
