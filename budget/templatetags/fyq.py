from datetime import datetime

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def fyq(date_value):
	try:
		year = int(date_value.year)
		month = int(date_value.month)
	except:
		return ''
	
	if month>=10: # Digi's fiscal year starts in October. jjb factor_this
		year = year + 1
		
	if month>=10:
		quarter = 1
	elif month >= 7:
		quarter = 4
	elif month >= 4:
		quarter = 3
	elif month >= 1:
		quarter = 2
		
	return "Q" + str(quarter) + "FY" + str(year)[-2:]
		
	