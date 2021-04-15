from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


name_symbols_validator = RegexValidator(
    regex=r"^[a-zA-Zа-яА-Я0-9 'іїёєґЄЇҐІЭ.`-]*$",
    message=_("Only alphanumeric characters, digits, and '-. are allowed")
)

two_in_row_validator = RegexValidator(
    regex=r"(.)\1{2,}",
    inverse_match=True,
    message=_("No more than 2 identical symbols in a row are allowed")
)

iban_validator = RegexValidator(
    regex=r'^[A-Za-z]{2}\d{27}$',
    message=_('Wrong IBAN format')
)

mfo_validator = RegexValidator(
    regex=r'^\d{6}$',
    message=_('Wrong MFO format')
)
