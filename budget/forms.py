from django import forms
from budget.models import HomologationItem, HomologationStatus

class StatusDateForm(forms.Form):
    requested_start = forms.DateField(required=False, label='Requested Start')
    approved_for    = forms.DateField(required=False, label='Approved For')
    ready           = forms.DateField(required=False, label='Ready')
    started         = forms.DateField(required=False, label='Started')
    completed       = forms.DateField(required=False, label='Completed')

class StatusAmountForm(forms.Form):
    budget_amount   = forms.IntegerField(required=False, label='Budget Amount')
    quoted_amount   = forms.IntegerField(required=False, label='Quoted Amount')
    actual_amount   = forms.IntegerField(required=False, label='Actual Amount')

class EditItemForm(forms.Form):
    name            = forms.CharField(required=True,  label='Name')
    project_code    = forms.CharField(required=True,  label='Project Code')
    description     = forms.CharField(required=False,  label='Description')
    cert_type       = forms.ChoiceField(required=True,  label='Cert Type', choices=HomologationItem.CERT_TYPES)
    region          = forms.ChoiceField(required=True,  label='Region', choices=HomologationItem.CERT_REGION_TYPES)
    supplier        = forms.CharField(required=False,  label='Supplier')
    module          = forms.CharField(required=False,  label='Module')
    
    approval_status = forms.ChoiceField(required=True,  label='Approval', choices=HomologationStatus.CERT_APPROVAL_STATUS)
    certification_status = forms.ChoiceField(required=True,  label='Cert Status', choices=HomologationStatus.CERT_STATUS)

    requested_start = forms.DateField(required=False, label='Requested Start')
    approved_for    = forms.DateField(required=False, label='Approved For')
    ready           = forms.DateField(required=False, label='Ready')
    started         = forms.DateField(required=False, label='Started')
    completed       = forms.DateField(required=False, label='Completed')
    
    budget_amount   = forms.IntegerField(required=False, label='Budget Amount')
    quoted_amount   = forms.IntegerField(required=False, label='Quoted Amount')
    actual_amount   = forms.IntegerField(required=False, label='Actual Amount')

