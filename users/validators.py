from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


validate_iban = RegexValidator(regex='UA\\d{8}[A-Z0-9]{19}',
                                   message = _('This field must contain 29 characters, numbers and Latin'),
                                   code = 'invalid_iban')

validate_edrpou = RegexValidator(regex='^[0-9]{8}$',
                                   message = _('This field must contain 8 characters, only numbers'),
                                   code = 'invalid_edrpou')