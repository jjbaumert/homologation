from django import template
from datetime import datetime

register = template.Library()

@register.filter
def datef(date_value):
    try:
        str = datetime.strftime(date_value,"%Y-%m-%d")
    except:
        return ''
	
    return str

