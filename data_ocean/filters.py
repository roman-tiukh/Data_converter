import django_filters
from django.utils.translation import ugettext_lazy as _
from django.utils.text import format_lazy
from rest_framework.exceptions import ValidationError
from django_filters.widgets import BooleanWidget

from .models import Register


class ValidatedBooleanWidget(BooleanWidget):

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if value:
            if isinstance(value, str):
                value = value.lower()
            if value not in ('true', 'false', '1', '0'):
                reason = _('is invalid request parameter. Could be true, false, 1, 0')
                raise ValidationError({
                    name: format_lazy('{value} {reason}', value=value, reason=reason)
                })
        return {
            '1': True,
            '0': False,
            'true': True,
            'false': False,
            True: True,
            False: False,
        }.get(value, None)


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
