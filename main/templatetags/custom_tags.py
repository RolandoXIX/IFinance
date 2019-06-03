from django import template
from main.models import Account
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat

register = template.Library()

@register.simple_tag
def category_method(obj, method, year, month):
    return intcomma(floatformat(abs(getattr(obj, method)(year, month)),2))

@register.simple_tag
def category_method_abs(obj, method, year, month):
    return intcomma(floatformat(getattr(obj, method)(year, month),2))

@register.filter(name='abs')
def abs_filter(value):
    return abs(value)