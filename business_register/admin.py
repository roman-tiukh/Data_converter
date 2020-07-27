from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from business_register.models.kved_models import Kved, KvedGroup, KvedDivision, KvedSection
from business_register.models.fop_models import Fop
from business_register.models.company_models import Company

admin.site.register(Fop)
admin.site.register(Kved)
admin.site.register(KvedGroup)
admin.site.register(KvedDivision)
admin.site.register(KvedSection)
admin.site.register(Company, SimpleHistoryAdmin)
