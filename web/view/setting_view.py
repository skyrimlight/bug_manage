from django.shortcuts import render, HttpResponse, redirect

from untils.tencent.cos import delete_cos
from web import models


def setting(request, project_id):
    # form
    return render(request, 'setting.html')


def setting_delete(request, project_id):
    if request.method == 'GET':
        return render(request, 'setting_delete.html')
    project_name = request.POST.get('project_name')
    project_delete = models.Project.objects.filter(name=project_name, creator=request.tracer.user).first()
    if not project_delete:
        return render(request, 'setting_delete.html', {'error': '项目名错误或非项目创建者'})
    # 1.删除桶
    delete_cos(request.tracer.project.bucket)
    # 2.删除数据库数据
    # print(part_obj)
    models.Project.objects.filter(id=request.tracer.project.id).delete()
    return redirect('project_list')
