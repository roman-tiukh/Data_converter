from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def send_report():
    print('****************')
    print('*  Send report  *')
    print('****************')

    from data_ocean.emails import send_reports_mail
    send_reports_mail()

    print('*** Task update_pep send_report. ***')
