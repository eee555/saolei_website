from django import forms


class TournamentForm(forms.Form):
    name = forms.JSONField(required=True)
    description = forms.JSONField()
    start_time = forms.DateField(required=True)
    end_time = forms.DateField(required=True)
