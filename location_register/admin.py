from django.contrib import admin

from data_ocean.admin import RegisterModelAdmin
from location_register.models.address_models import Country
from location_register.models.koatuu_models import (KoatuuFirstLevel, KoatuuSecondLevel,
                                                    KoatuuThirdLevel, KoatuuFourthLevel)
from location_register.models.ratu_models import RatuStreet
from location_register.models.drv_models import DrvBuilding


@admin.register(Country)
class CountryAdmin(RegisterModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

    def has_add_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(KoatuuFirstLevel)
class KoatuuFirstLevellAdmin(RegisterModelAdmin):
    list_display = (
        'name',
        'code'
    )

    search_fields = ('name', 'code')
    ordering = ('updated_at',)


@admin.register(KoatuuSecondLevel)
class KoatuuSecondLevelAdmin(RegisterModelAdmin):
    list_display = (
        'name',
        'code',
        'category'
    )

    search_fields = ('name', 'code')
    ordering = ('updated_at',)
    list_filter = ('category',)


@admin.register(KoatuuThirdLevel)
class KoatuuThirdLevelAdmin(RegisterModelAdmin):
    list_display = (
        'name',
        'code',
        'category'
    )

    search_fields = ('name', 'code')
    ordering = ('updated_at',)
    list_filter = ('category',)


@admin.register(KoatuuFourthLevel)
class KoatuuFourthLevelAdmin(RegisterModelAdmin):
    list_display = (
        'name',
        'code',
        'category'
    )

    search_fields = ('name', 'code')
    ordering = ('updated_at',)
    list_filter = ('category',)


@admin.register(RatuStreet)
class RatuStreetAdmin(RegisterModelAdmin):
    list_display = (
        'name',
        'code',
        'citydistrict',
        'city',
        'district',
        'region'
    )
    search_fields = ('name', 'code')
    ordering = ('updated_at',)
    list_filter = ('region',)


@admin.register(DrvBuilding)
class DrvBuildingAdmin(RegisterModelAdmin):
    list_display = (
        'number',
        'code',
        'zip_code',
        'street',
        'council',
        'region'
    )
    search_fields = ('number', 'code', 'street')
    ordering = ('updated_at',)
    list_filter = ('region', 'district', 'council', 'ato', 'street')
