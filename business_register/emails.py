from django.conf import settings

from business_register.models.company_models import CompanyType
from data_converter.email_utils import send_template_mail


def send_new_company_type_message(company_type: CompanyType):
    send_template_mail(
        to=settings.DEVELOPER_EMAILS,
        subject='Новий тип компанії додано',
        template='business_register/emails/new_company_type.html',
        context={
            'company_type': company_type,
        }
    )
