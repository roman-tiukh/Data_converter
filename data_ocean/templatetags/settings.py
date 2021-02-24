from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_support_email():
    return settings.SUPPORT_EMAIL
