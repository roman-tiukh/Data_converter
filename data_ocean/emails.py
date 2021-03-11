from django.conf import settings

from data_converter.email_utils import send_template_mail
from data_ocean.models import Report


def send_reports_mail():
    send_template_mail(
        to=settings.REPORT_EMAILS,
        subject='Звіт про оновлення реєстрів за останні 24 години',
        template='data_ocean/emails/report.html',
        context={
            'reports': Report.collect_last_day_reports()
        }
    )
