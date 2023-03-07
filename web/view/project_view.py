from time import time

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from web import models
from web.forms.project import ProjectModelForm
from untils.tencent.cos import create_bucket


def project_list(request):
    if request.method == 'GET':
        form = ProjectModelForm(request)
        project_dict_star = []
        project_dict_my = models.Project.objects.filter(creator=request.tracer.user).all()
        for i in project_dict_my:
            if i.star:
                project_dict_star.append(i)
        project_dict_my = project_dict_my.filter(star=False).all()
        project_dict_join = models.ProjectUser.objects.filter(user=request.tracer.user.id).all()
        for i in project_dict_join:
            if i.star:
                project_dict_star.append(i.project)
        project_dict_join = project_dict_join.filter(star=False).all()
        color_choice = [[1, "#56b8eb"], [2, "#f28033"], [3, "#ebc656"], [4, "#a2d148"], [5, "#20BFA4"], [6, "#7461c2"],
                        [7, "#20bfa3"]]
        context = {
            "form": form,
            'project_dict_star': project_dict_star,
            'project_dict_my': project_dict_my,
            'project_dict_join': project_dict_join, 'color_choice': color_choice
        }
        # return render(request, 'project_list_test.html', context=context)
        return render(request, 'project_list.html', context=context)
    form = ProjectModelForm(request, request.POST)
    # creator = models.UserInfo.objects.filter(id=request.tracer.user.id).first()
    # color = request.POST.get('color')
    if form.is_valid():
        bucket_name = f'{request.tracer.user.id}-{int(time())}-1302221415'
        region = 'ap-nanjing'
        create_bucket(bucket=bucket_name, region=region)
        form.instance.bucket = bucket_name
        form.instance.region = region
        form.instance.creator = request.tracer.user
        instance = form.save()
        issues_type_object_list = []
        for i in models.IssuesType.PROJECT_INIT_LIST:
            issues_type_object_list.append(models.IssuesType(title=i, project=instance))
        models.IssuesType.objects.bulk_create(issues_type_object_list)  # 批量添加
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    """
    项目添加星标
    :param request:
    :param project_type:
    :param project_id:
    :return:
    """
    if project_type == 'my':
        # form = models.Project.objects.filter(id=project_id).first()
        models.Project.objects.filter(id=project_id).update(star=True)
    elif project_type == 'join':
        # form = models.ProjectUser.objects.filter(project=project_id).first()
        print(1111111111111111)
        models.ProjectUser.objects.filter(id=project_id).update(star=True)
    else:
        return HttpResponse('错误请求')
    # if form.star:
    #     form.star = False
    # else:
    #     form.star = True
    # form.save()
    return redirect('project_list')


def project_unstar(request, project_id):
    """
        项目取消星标
    :param request:
    :param project_id:
    :return:
    """
    project_info = models.Project.objects.filter(id=project_id).first()
    if project_info.star:
        project_info.star = False
        project_info.save()
    else:
        models.ProjectUser.objects.filter(project=project_id).update(star=False)
    return redirect('project_list')
