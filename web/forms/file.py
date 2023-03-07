from django.core.exceptions import ValidationError
from django import forms

from untils.bootstrap import BootStrapModelForm
from untils.tencent.cos import check_etag
from web import models
from web.models import FileRepository


class FileModelForm(BootStrapModelForm):
    class Meta:
        model = FileRepository
        fields = ['name']

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    def clean_name(self):
        name = self.cleaned_data['name']
        queryset = models.FileRepository.objects.filter(project=self.request.tracer.project, name=name, file_type=True)
        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object)
        else:
            exists = queryset.filter(parent__isnull=True)
        if exists:
            raise ValidationError('文件夹已存在')
        return name


class FileUpdateModelForm(BootStrapModelForm):
    etag = forms.CharField(label='Etag')
    parent = forms.CharField

    class Meta:
        model = FileRepository
        exclude = ['project', 'file_type', 'update_user', 'update_datetime', 'parent']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_file_path(self):
        return f'https://{self.cleaned_data["file_path"]}'

    # def clean(self):
    #     etag = self.cleaned_data["etag"]
    #     key = self.cleaned_data["key"]
    #     size = self.cleaned_data["size"]
    #     if not key or not etag:
    #         return self.cleaned_data
    #     try:
    #         result = check_etag(bucket=self.request.tracer.project.bucket, key=key)
    #     except Exception:
    #         self.add_error('key', '文件不存在')
    #         # result
    #         self.cleaned_data
    #     cos_etag = result.get('Etag')
    #     if cos_etag != etag:
    #         self.add_error('etag', 'Etag错误')
    #     cos_length = result.get('Content-Length')
    #     if int(cos_length) != size:
    #         self.add_error('size', '大小不一致')
    #     return self.cleaned_data
