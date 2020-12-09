from django.core.management.base import BaseCommand
from payment_system.models import ProjectSubscription


class Command(BaseCommand):
    help = 'Update expire subscriptions'

    def handle(self, *args, **options):
        message = ProjectSubscription.update_expire_subscriptions()
        self.stdout.write(message, ending='\n')
