from crispy_forms import helper
from crispy_forms.layout import Submit
from django import forms
from django.core.validators import MinValueValidator

from .models import RESPONDER, DECISIONS


class EmailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-success btn-block mt-4'))

    email = forms.EmailField()
    experience = forms.ChoiceField(choices=RESPONDER)


class PatternCheck(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.field_class = 'ml-4'
        self.helper.label_class = 'ml-4'

    case_id = forms.IntegerField(widget=forms.HiddenInput())
    is_normal_cd13cd11b = forms.ChoiceField(
        choices=DECISIONS[:3],
        widget=forms.RadioSelect,
        label="Нормальный ли этот паттерн?"
    )
    is_normal_cd13cd16 = forms.ChoiceField(
        choices=DECISIONS,
        widget=forms.RadioSelect,
        label="Нормальный ли этот паттерн?"
    )
    is_normal_cd11bcd16 = forms.ChoiceField(
        choices=DECISIONS,
        widget=forms.RadioSelect,
        label="Нормальный ли этот паттерн?"
    )


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-success btn-block mt-4'))
    case_number = forms.IntegerField(validators=[MinValueValidator(1)])
