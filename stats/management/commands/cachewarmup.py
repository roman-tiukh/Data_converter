from django.core.management.base import BaseCommand
from stats.tasks import cache_warm_up


class Command(BaseCommand):
    help = 'Cache warming up for stats for now.'

    def handle(self, *args, **options):
        cache_warm_up()
