from django.db.models import ImageField
from django.forms import forms
from django.template.defaultfilters import filesizeformat


class RestrictedImageField(ImageField):
    def __init__(self, *args, **kwargs):
        self.max_upload_size = kwargs.pop("max_upload_size", [])
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        file = data.file

        try:
            if file.size > self.max_upload_size:
                raise forms.ValidationError('上传图片大小不能超过 %(max_size)s， 当前图片大小 %(file_size)s。',
                                            params={"max_size": filesizeformat(self.max_upload_size),
                                                    "file_size": filesizeformat(file.size)})
        except AttributeError:
            pass
        return data
