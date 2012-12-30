from django import template
from datetime import datetime

register = template.Library()

@register.filter
def datetimef(date_value):
    try:
        str = datetime.strftime(date_value,"%Y-%m-%d %H:%M %p")
        if str[-2:]=='AM':
            str=str[:-3]+'a'
        else:
            str=str[:-3]+'p'
    except:
        return ''
	
    return str

