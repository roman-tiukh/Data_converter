import datetime
# from django.utils import timezone
from django.core.management.base import BaseCommand
from users.models import CandidateUserModel


class Command(BaseCommand):
    help = 'Remove expire Candidates'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        # now = timezone.now()
        CandidateUserModel.objects.filter(expire_at__lt=now).delete()
