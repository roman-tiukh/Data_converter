from django.contrib import admin
from data_ocean.models import Register


@admin.register(Register)
class AdminRegister(admin.ModelAdmin):
    list_display = (
        'name',
        'total_records',
        'status'
    )

    search_fields = ('name',)
    ordering = ('id',)
    list_filter = ('status',)

