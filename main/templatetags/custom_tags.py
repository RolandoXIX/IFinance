from django import template
from main.models import Account
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
from main import services

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

@register.simple_tag
def call_service(method, *args):
    return intcomma(floatformat(getattr(services, method)(*args)),2)