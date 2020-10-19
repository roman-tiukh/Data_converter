from django.conf import settings
from django.db import models
from data_ocean.models import DataOceanModel


class Project(DataOceanModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True)
    token = models.CharField(max_length=40, null=True)
    disabled = models.BooleanField(default=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Subscription(DataOceanModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=500, null=True)
    price = models.SmallIntegerField(default=0)
    requests_limit = models.IntegerField('limit for API requests from the project', default=0)
    duration = models.SmallIntegerField(default=30)
    grace_period = models.SmallIntegerField(null=True, default=0)


class Invoice(DataOceanModel):
    paid_at = models.DateField(null=True)
    # this field is for an accountant`s notes
    info = models.CharField(max_length=500, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                related_name='project_invoices')
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE,
                                     related_name='subscription_invoices')


class ProjectSubscription(DataOceanModel):
    STATUSES = [
        ('active', 'active'),
        ('past', 'past'),
        ('future', 'future'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUSES, max_length=10)
    expiring_date = models.DateField(null=True)

    class Meta:
        verbose_name = "relation between the project and the user"
