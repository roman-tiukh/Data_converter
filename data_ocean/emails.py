from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from data_converter.email_utils import send_template_mail
from data_ocean.models import Register, Report
from users.models import DataOceanUser


def send_reports_mail():
    reports = Report.collect_last_day_reports()
    not_working = []
    for register in list(Register.objects.exclude(in_daily_report=None).values('in_daily_report')):
        if all(register['in_daily_report'] != report.registry_name for report in reports):
            not_working.append(register['in_daily_report'])
    send_template_mail(
        to=settings.REPORT_EMAILS,
        subject='Звіт про оновлення реєстрів за останні 24 години',
        template='data_ocean/emails/report.html',
        context={
            'reports': reports,
            'not_working': not_working
        }
    )


def send_export_url_file_path_message(user: DataOceanUser, link: str):
    send_template_mail(
        to=[user.email],
        subject=_('Generation of .xlsx export file completed'),
        template='data_ocean/emails/export_to_xlsx_completed.html',
        context={
            'user': user,
            'link': link
        }
    )
