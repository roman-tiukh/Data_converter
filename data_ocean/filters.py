import django_filters
from data_ocean.models import Register


class RegisterFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        fields=(
            ('id', 'name', 'source_last_update')
        )
    )

    class Meta:
        model = Register
        fields = {
            'name': ['icontains'],
            'source_register_id': ['exact'],
            'source_last_update': ['exact', 'gt', 'lt'],
        }
