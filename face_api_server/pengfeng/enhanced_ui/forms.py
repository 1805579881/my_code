from django import forms


def suffix_validator(value):
    a = value
    pass


class FaceDataBatchUploadForm(forms.Form):
    file = forms.FileField(required=True, label='数据备份', help_text='打包压缩后的人脸数据文件', validators=[suffix_validator],
                           widget=forms.FileInput(attrs={'accept': 'application/zip'}))
