from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DataOceanUser
from payment_system.models import Project
from django.conf import settings


@receiver(post_save, sender=DataOceanUser)
def user_post_save_signal(sender, **kwargs):
    created: bool = kwargs['created']
    user: DataOceanUser = kwargs['instance']

    if created:
        Project.create(
            owner=user,
            name=settings.DEFAULT_PROJECT_NAME,
            description=settings.DEFAULT_PROJECT_DESCRIPTION,
            is_default=True,
        )
