from __future__ import absolute_import, unicode_literals

from celery import shared_task

from payment_system.models import ProjectSubscription, InvoiceDailyReport


@shared_task
def update_project_subscriptions():
    print('******************************')
    print('*    Update subscriptions    *')
    print('******************************')

    message = ProjectSubscription.update_expire_subscriptions()

    print(message)


@shared_task
def create_daily_report():
    print('*********************************')
    print('*  Create daily payment report  *')
    print('*********************************')

    InvoiceDailyReport.create_daily_report()
    print('*** Created daily payment report ***')
