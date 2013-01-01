import django_tables2 as tables
from budget.models import HomologationStatus
from django.utils.html import mark_safe
from budget.templatetags.fyq import fyq

class HomologationTable(tables.Table):
    name = tables.Column(verbose_name='name', accessor='homologation_item')
    cert_type = tables.Column(verbose_name='cert type', accessor='homologation_item.cert_type')
    module = tables.Column(verbose_name='module', accessor='homologation_item.module')
    budget_amount = tables.Column(verbose_name='budgeted')

    def render_name(self, value, record):
        return mark_safe('<a href="/budget/%s">%s</a>''' % (record.homologation_item.id, record.homologation_item.name))

    def render_requested_start(self, value, record):
        return fyq(value) 

    def render_approved_for(self, value, record):
        return fyq(value) 

    class Meta:
        model = HomologationStatus
        attrs = {"class": "paleblue"}

        sequence = ('requested_start','approved_for',
            'name','cert_type','module','approval_status',
            'certification_status', 'budget_amount')

        exclude = ('id','homologation_item','active_record','updated','update_reason','quoted_amount',
            'actual_amount','ready','started','completed')

        order_by = ('-requested_start', '-budget_amount')
