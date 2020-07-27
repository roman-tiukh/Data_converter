from django.db import models
from users.models import DataOceanUser


class ApiUsageTracking(models.Model):
    user = models.ForeignKey(
        DataOceanUser, models.CASCADE, verbose_name='користувач',
        related_name='api_usage',
    )
    timestamp = models.DateTimeField('мітка часу', auto_now_add=True)
    pathname = models.CharField('шлях', max_length=250)

    class Meta:
        db_table = 'stats_api_usage_tracking'
        verbose_name = 'використання API'
