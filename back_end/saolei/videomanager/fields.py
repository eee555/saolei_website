from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat


class RestrictedFileField(FileField):
    """ max_upload_size:
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 1024*1024*5)
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)   # clean()方法来自于FileField的父类Field, 用于验证
        file = data.file

        try:
            content_type = file.content_type
            # 自定义验证
            if content_type in self.content_types:
                if file.size > self.max_upload_size:
                    raise forms.ValidationError('Please keep filesize under {}. Current filesize {}'.format(filesizeformat(self.max_upload_size), filesizeformat(file.size)))
            else:
                raise forms.ValidationError('This file type is not allowed.')
        except AttributeError:
            pass
        return data
