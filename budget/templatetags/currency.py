from django import template

register = template.Library()

@register.filter
def currency(int_value):
    try:
        return '{:20,.0f}'.format(int(int_value))
    except:
        return ''
