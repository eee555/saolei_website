from django import forms


class UploadVideoForm(forms.Form):
    file = forms.FileField(
        max_length=100, allow_empty_file=False, required=True)
