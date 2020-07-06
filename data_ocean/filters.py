import django_filters

class RegisterFilter(django_filters.FilterSet):
    source_last_update = django_filters.DateFromToRangeFilter()
    o = django_filters.OrderingFilter(
        fields=(
            ('id', 'name', 'source_last_update')
        )
    )
