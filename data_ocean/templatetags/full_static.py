from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_frontend_url():
    return settings.FRONTEND_SITE_URL or 'https://dp.dataocean.us'


@register.simple_tag
def get_backend_url():
    return settings.BACKEND_SITE_URL or 'https://ipa.dataocean.us'
