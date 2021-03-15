from django.conf import settings

from business_register.models.company_models import CompanyType
from data_converter.email_utils import send_template_mail
from users.models import DataOceanUser


def send_new_company_type_message(company_type: CompanyType):
    send_template_mail(
        to=settings.DEVELOPER_EMAILS,
        subject='Новий тип компанії додано - потрібний переклад',
        template='business_register/emails/new_company_type.html',
        context={
            'company_type': company_type,
        }
    )


def send_export_url_file_path_message(user_id: int, link: str):
    user = DataOceanUser(id=user_id)
    send_template_mail(
        to=[user.email],
        subject='Generation of .xlsx export file completed',
        template='business_register/emails/export_to_xlsx_completed.html',
        context={
            'user': user,
            'link': link
        }
    )
