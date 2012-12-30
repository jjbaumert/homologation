from django import forms

class StatusDateForm(forms.Form):
    requested_start = forms.DateField(required=False, label='Requested Start')
    approved_for    = forms.DateField(required=False, label='Approved For')
    ready           = forms.DateField(required=False, label='Ready')
    started         = forms.DateField(required=False, label='Started')
    completed       = forms.DateField(required=False, label='Completed')

