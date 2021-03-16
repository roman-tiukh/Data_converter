from django.core.management.base import BaseCommand
from django.utils import timezone

from payment_system.models import ProjectSubscription, Invoice, Subscription
from users.models import DataOceanUser


class Command(BaseCommand):
    help = 'Update expire subscriptions'

    def handle(self, *args, **options):
        ps = ProjectSubscription(
            grace_period=30,
            periodicity=Subscription.MONTH_PERIOD,
        )
        user = DataOceanUser(
            first_name='Test',
            last_name='Test',
            email='test@test.net',
            language='uk',
        )
        invoice = Invoice(
            project_subscription=ps,
            start_date=timezone.localdate(),
            subscription_name='Custom for 1 year',
            project_name='Project 1',
            price=36000,
            created_at=timezone.now(),
        )
        bytes_io = invoice.get_pdf(user)
        with open('test_invoice.pdf', 'wb') as file:
            file.write(bytes_io.read())
        print('Success')
