from __future__ import absolute_import, unicode_literals

from celery import shared_task

from payment_system.models import ProjectSubscription


@shared_task
def update_project_subscriptions():
    print('******************************')
    print('*    Update subscriptions    *')
    print('******************************')

    message = ProjectSubscription.update_expire_subscriptions()

    print(message)
