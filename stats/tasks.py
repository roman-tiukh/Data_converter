from __future__ import absolute_import, unicode_literals
import logging

import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import caches

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

warm_endpoints = [
    '/api/pep/',
    '/api/company/',
    '/api/company/ukr/',
    '/api/company/uk/',
    '/api/fop/',
]


def endpoints_cache_warm_up(endpoints=None):
    if 'counts' not in settings.CACHES:
        return
    if endpoints is None:
        endpoints = warm_endpoints
    cache = caches['counts']
    for endpoint in endpoints:
        cache.delete_pattern(f'{endpoint}*')
        response = requests.get(f'{settings.BACKEND_SITE_URL}{endpoint}', headers={
            'Authorization': f'Service {settings.SERVICE_TOKEN}'
        })
        if response.status_code != 200:
            logger.error(f'{endpoint} warming failed, status={response.status_code}, body={response.text}')


def cache_warm_up():
    endpoints_cache_warm_up()

    logger.info('Start cache warming')
    for view in warm_views:
        view.warm_up_cache()
        logger.info(f'{view.get_cache_key()} warmed up successfully')
    logger.info('End cache warming')


@shared_task
def cache_warming_up():
    cache_warm_up()
