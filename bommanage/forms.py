
from django import forms

class BomSearchForm(forms.Form):
    part_number = forms.RegexField(regex=r'^[0-9]{5,8}(-[0-9]{1,2})?$', label='Part Number')

    possibilities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(),required=False)
