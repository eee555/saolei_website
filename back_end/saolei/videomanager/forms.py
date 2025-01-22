from django import forms
from .models import VideoModel
from config.global_settings import MaxSizes


class UploadVideoForm(forms.ModelForm):
    file = forms.FileField(
        max_length=100, allow_empty_file=False, required=True)
    # upload_time = forms.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    review_code = forms.IntegerField(max_value=255, min_value=0, required=True)
    identifier = forms.CharField(max_length=MaxSizes.identifier, required=True)
    stnb = forms.FloatField(min_value=0.0, required=True)
    rqp = forms.FloatField(min_value=0.0, required=True)

    class Meta:
        model = VideoModel
        fields = ['software', 'level', 'mode', 'timems', 'bv', 'left', 'right', 'double', 'left_ce', 'right_ce', 'double_ce', 'path', 'flag', 'op', 'isl', 'cell0', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8']
