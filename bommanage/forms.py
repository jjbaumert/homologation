
from django import forms

class BomSearchForm(forms.Form):
    part_number = forms.RegexField(regex=r'^[0-9]{7,8}$', label='Part Number')

    possibilities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(),required=False)
