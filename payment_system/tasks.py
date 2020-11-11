from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.utils.timezone import localdate

from payment_system.constants import DEFAULT_SUBSCRIPTION_NAME
from payment_system.models import ProjectSubscription


@shared_task
def update_project_subscriptions():
    print('********************')
    print('*    Update subscriptions    *')
    print('********************')

    update_project_subscriptions = (ProjectSubscription.objects
                                    .filter(expiring_date=localdate())
                                    .exclude(subscription__name=DEFAULT_SUBSCRIPTION_NAME))
    if not update_project_subscriptions:
        print('*** No project__subscriptions to update. ***')
        return
    for project_subscription in update_project_subscriptions:
        project_subscription.status = ProjectSubscription.PAST
        project_subscription.save(update_fields=['status'])
        next_project_subscription = ProjectSubscription.objects.filter(
            project=project_subscription.project,
            status=ProjectSubscription.FUTURE
        ).first()
        if next_project_subscription:
            next_project_subscription.status = ProjectSubscription.ACTIVE
            next_project_subscription.save(update_fields=['status'])

    print('*** Task update_project_subscriptions is done. ***')
