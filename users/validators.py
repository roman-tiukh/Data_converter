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

validate_iban = RegexValidator(regex='^UA\\d{8}[A-Z0-9]{19}$',
                                   message = _('This field must contain 29 characters, numbers and Latin'))

validate_edrpou = RegexValidator(regex='^[0-9]{8}$',
                                   message = _('This field must contain 8 characters, only numbers'))