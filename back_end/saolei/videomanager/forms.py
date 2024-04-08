from django import forms
from .models import VideoModel
from django.contrib.auth.models import User


class UploadVideoForm(forms.Form):
    file = forms.FileField(
        max_length=100, allow_empty_file=False, required=True)
    # upload_time = forms.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    review_code = forms.IntegerField(max_value=255, min_value=0, required=True)
    software = forms.CharField(max_length=1, required=True)
    level = forms.CharField(max_length=1, required=True)
    mode = forms.CharField(max_length=2, required=True)
    timems = forms.IntegerField(required=True)
    bv = forms.IntegerField(max_value=32767, min_value=1, required=True)
    bvs = forms.FloatField(min_value=0.0, required=True)

    designator = forms.CharField(max_length=80, required=True)
    left = forms.IntegerField(max_value=32767, min_value=0, required=True)
    right = forms.IntegerField(max_value=32767, min_value=0, required=True)
    double = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cl = forms.IntegerField(max_value=32767, min_value=0, required=True)
    left_s = forms.FloatField(min_value=0.0, required=True)
    right_s = forms.FloatField(min_value=0.0, required=True)
    double_s = forms.FloatField(min_value=0.0, required=True)
    cl_s = forms.FloatField(min_value=0.0, required=True)
    path = forms.FloatField(min_value=0.0, required=True)
    flag = forms.IntegerField(max_value=32767, min_value=0, required=True)
    flag_s = forms.FloatField(min_value=0.0, required=True)
    stnb = forms.FloatField(min_value=0.0, required=True)
    rqp = forms.FloatField(min_value=0.0, required=True)
    ioe = forms.FloatField(min_value=0.0, required=True)
    thrp = forms.FloatField(min_value=0.0, required=True)
    corr = forms.FloatField(min_value=0.0, max_value=1.0, required=True)
    ce = forms.IntegerField(max_value=32767, min_value=0, required=True)
    ce_s = forms.FloatField(min_value=0.0, required=True)
    op = forms.IntegerField(max_value=32767, min_value=0, required=True)
    isl = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell0 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell1 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell2 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell3 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell4 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell5 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell6 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell7 = forms.IntegerField(max_value=32767, min_value=0, required=True)
    cell8 = forms.IntegerField(max_value=32767, min_value=0, required=True)
