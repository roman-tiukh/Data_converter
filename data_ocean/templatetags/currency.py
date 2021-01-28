from django import template
from data_ocean.utils import uah2words as u2w

register = template.Library()


@register.filter
def uah2words(value):
    return u2w(value)
