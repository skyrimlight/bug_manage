from untils.bootstrap import BootStrapModelForm
from web import models


class WikiModelForm(BootStrapModelForm):
    class Meta:
        model = models.Wiki
        exclude = ['depth', 'project']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        result_list = [("", "请选择")]
        project_list = models.Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        result_list.extend(project_list)
        self.fields['parent'].choices = result_list
