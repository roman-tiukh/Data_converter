from django_filters import compat
from django_filters.rest_framework import DjangoFilterBackend, filters


class DODjangoFilterBackend(DjangoFilterBackend):
    def get_coreschema_field(self, field):
        if isinstance(field, filters.NumberFilter):
            field_cls = compat.coreschema.Number
        elif isinstance(field, filters.BooleanFilter):
            field_cls = compat.coreschema.Boolean
        else:
            field_cls = compat.coreschema.String
        return field_cls(
            description=str(field.extra.get('help_text', ''))
        )
