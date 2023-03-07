from django import forms

from untils.bootstrap import BootStrapModelForm
from web import models
from web.models import Issues


class IssuesModelForm(BootStrapModelForm):
    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        # 单独添加样式和属性
        widgets = {
            "assign": forms.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            "attention": forms.SelectMultiple(
                attrs={'class': 'selectpicker', 'data-live-search': 'true', 'data-actions-box': 'true'}),
            'parent': forms.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(
            project=request.tracer.project).values_list('id', 'title')

        parent_object_list = models.Issues.objects.filter(project=request.tracer.project).values_list('id', 'subject')
        parent_list = [("", "-------")]
        parent_list.extend(parent_object_list)
        self.fields['parent'].choices = parent_list
        module_list = [("", "-------"), ]
        module_object_list = models.Module.objects.filter(project=request.tracer.project).values_list('id', 'title')
        # self.fields['attention'].choices = models.ProjectUser.
        module_list.extend(module_object_list)
        # self.fields['mode'].choices = module_list
        # 处理人和关注人
        assign_list = [("", "-------"), (request.tracer.project.creator.id, request.tracer.project.creator.username)]
        assign_obj_list = models.ProjectUser.objects.filter(project=request.tracer.project).values_list('user_id',
                                                                                                        'user__username')
        assign_list.extend(assign_obj_list)
        self.fields['assign'].choices = assign_list
        self.fields['attention'].choices = assign_list

        # 关联问题
        issues_list = [("", "-------")]
        issues_obj_list = models.Issues.objects.filter(project=request.tracer.project).values_list('id', 'subject')
        issues_list.extend(issues_obj_list)
        self.fields['parent'].choices = issues_list


class IssuesReplyModelForm(BootStrapModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']
