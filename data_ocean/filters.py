import django_filters
from .models import Register


class RegisterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    source_name = django_filters.CharFilter(lookup_expr='icontains')
    updated_at = django_filters.DateFromToRangeFilter()
    o = django_filters.OrderingFilter(
        fields=(
            ('id', 'name', 'source_last_update')
        )
    )

    class Meta:
        model = Register
        fields = ()
