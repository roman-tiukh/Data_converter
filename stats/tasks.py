from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task
from stats import views as stats_views


logger = logging.getLogger(__name__)


warm_views = [
    stats_views.CompanyTypeCountView,
    stats_views.TopKvedsView,
    stats_views.RegisteredCompaniesCountView,
    stats_views.RegisteredFopsCountView,
    stats_views.PepsCountView,
    stats_views.PepRelatedPersonsCountView,
    stats_views.PepLinkedCompaniesCountView,
    stats_views.PepRelationCategoriesCountView,
]


def cache_warm_up():
    logger.info('Start cache warming')
    for view in warm_views:
        view.warm_up_cache()
        logger.info(f'{view.get_cache_key()} warmed up successfully')
    logger.info('End cache warming')


@shared_task
def cache_warming_up():
    cache_warm_up()
