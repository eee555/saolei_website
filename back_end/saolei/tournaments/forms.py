from django import forms
from config.text_choices import Tournament_TextChoices

class TournamentForm(forms.Form):
    name = forms.JSONField(required=True)
    description = forms.JSONField()
    start_time = forms.DateField(required=True)
    end_time = forms.DateField(required=True)
    series = forms.ChoiceField(choices=Tournament_TextChoices.Series.choices, required=True)


