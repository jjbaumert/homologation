from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def currency(int_value):
	if int_value == None:
		return ''
	
	return '{:20,.0f}'.format(int(int_value))