from django import forms
from .models import VideoModel
from config.global_settings import MaxSizes


class UploadVideoForm(forms.Form):
    file = forms.FileField(
        max_length=100, allow_empty_file=False, required=True)
