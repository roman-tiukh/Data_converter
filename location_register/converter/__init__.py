from django.conf import settings

from data_ocean.models import Register

API_ADDRESS_FOR_DATASET = Register.objects.get(
        source_register_id=settings.LOCATION_KOATUU_SOURCE_REGISTER_ID
    ).source_api_address
