import json
import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, reverse, render
from django.views.decorators.csrf import csrf_exempt

from untils.tencent.cos import delete_bucket_one, delete_bucket_many, credential
from web import models
from web.forms.file import FileModelForm, FileUpdateModelForm


def file(request, project_id):
    """
    新建文件夹，修改文件夹名称
    :param request:
    :param project_id:
    :return:
    """
    file_parent_obj = None
    file_id = request.GET.get('folder', '')
    if file_id.isdecimal():
        file_parent_obj = models.FileRepository.objects.filter(id=int(file_id), file_type=True).first()
        file_object_list = models.FileRepository.objects.filter(parent=int(file_id),
                                                                project=request.tracer.project).order_by(
            '-file_type').all()
    else:
        file_object_list = models.FileRepository.objects.filter(parent__isnull=True,
                                                                project=request.tracer.project).order_by(
            '-file_type').all()
    if request.method == 'GET':
        breadcrumbs_list = []
        parent = file_parent_obj
        while parent:
            breadcrumbs_list.insert(0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent
        form = FileModelForm(request, file_parent_obj)
        folder_object = None
        if len(breadcrumbs_list) > 0:
            folder_object = breadcrumbs_list[-1]['id']
        content = {'form': form, 'file_object_list': file_object_list, 'breadcrumbs_list': breadcrumbs_list,
                   'folder_object': folder_object}
        return render(request, 'file.html', content)
    fid = request.POST.get('fid', '')
    file_obj = None
    if fid.isdecimal():
        file_obj = models.FileRepository.objects.filter(id=int(fid)).first()
    if file_obj:
        form = FileModelForm(request, file_parent_obj, data=request.POST, instance=file_obj)
    else:
        form = FileModelForm(request, file_parent_obj, data=request.POST)
    if form.is_valid():
        form.instance.parent = file_parent_obj
        form.instance.project = request.tracer.project
        form.instance.file_type = True
        form.instance.update_user = request.tracer.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def file_delete(request, project_id):
    """
    删除本地文件和文件夹以及cos端文件和文件夹
    :param request:
    :param project_id:
    :return:
    """
    fid = request.GET.get('fid', '')
    if not fid.isdecimal():
        return JsonResponse({'status': False, 'error': '文件或文件夹不存在'})
    file_obj = models.FileRepository.objects.filter(id=int(fid), project=request.tracer.project).first()
    # 判断是文件还是文件夹，分类删除
    if not file_obj.file_type:
        # 删除文件，归还空间
        request.tracer.project.use_space -= file_obj.file_size
        request.tracer.project.save()
        # cos删除文件
        delete_bucket_one(bucket=request.tracer.project.bucket, key=file_obj.key)
        # 数据库删除记录
        file_obj.delete()
    else:
        delete_file_list, temp_list, total_size = [], [], 0
        temp_list.append(file_obj.id)
        while temp_list:
            obj = models.FileRepository.objects.filter(parent_id=temp_list[0])
            for i in obj:
                if i.file_type:
                    temp_list.append(i.id)
                else:
                    total_size += i.file_size
                    delete_file_list.append({'Key': i.key})
            temp_list.pop(0)
        delete_bucket_many(bucket=request.project.bucket, key=delete_file_list)
        if total_size:
            request.tracer.project.use_space -= total_size
            request.tracer.project.save()
        file_obj.delete()

    return JsonResponse({'status': True})


def file_edit(request, project_id):
    pass


# @csrf_exempt
# def cos_credential(request, project_id):
#     """ 获取上传文件的临时凭证"""
#     print(1)
#     data_dict = credential(bucket=request.tracer.project.bucket)
#     print(2, data_dict)
#     return JsonResponse(data_dict)


@csrf_exempt
def cos_credential(request, project_id):
    """ 获取cos上传临时凭证 """
    per_file_limit = request.tracer.price_policy.per_file_size * 1024 * 1024
    total_file_limit = request.tracer.price_policy.project_space * 1024 * 1024
    files_info = json.loads(request.body.decode('utf-8'))
    # [{'name': '半泽直树.jpg', 'size': 240392}, {'name': '北竞王.jpg', 'size': 656459}]
    total_size = 0
    for i in files_info:
        if i['size'] > per_file_limit:
            return JsonResponse({'status': False,
                                 'error': f"当前套餐单文件最大为{request.tracer.price_policy.per_file_size}M，文件{i['name']}超出限制,请升级套餐。"})
        total_size += i['size']
        if total_size + request.tracer.project.use_space > total_file_limit:
            return JsonResponse({'status': False, 'error': "容量超过限制，请升级套餐。"})

    data_dict = credential(request.tracer.project.bucket)
    return JsonResponse({'status': True, 'data': data_dict})


@csrf_exempt
def file_post(request, project_id):
    """ 已上传成功的文件写入到数据 """
    """
    name: fileName,
    key: key,
    file_size: fileSize,
    parent: CURRENT_FOLDER_ID,
    # etag: data.ETag,
    file_path: data.Location
    """
    form = FileUpdateModelForm(request, data=request.POST)
    parent = request.POST.get('parent', '')
    if form.is_valid():
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update(
            {'project': request.tracer.project, 'file_type': False, 'update_user': request.tracer.user})
        if parent is not None and parent.isdecimal():
            data_dict.update({'parent_id': parent})
        instance = models.FileRepository.objects.create(**data_dict)
        request.tracer.project.use_space += data_dict['file_size']
        request.tracer.project.save()
        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime("%Y年%m月%d日 %H:%M"),
            'download_url': reverse('file_download', kwargs={"project_id": project_id, 'file_id': instance.id})
            # 'file_type': instance.get_file_type_display()
        }
        print(222222222)
        return JsonResponse({'status': True, 'data': result})
    print(11111111111111111)
    return JsonResponse({'status': False, 'data': "文件错误"})


def file_download(request, project_id, file_id):
    """ 下载文件 """
    # file_object = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    # res = requests.get(file_object.file_path)
    # data = res.content
    # response = HttpResponse(data)
    # response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_object.name)
    # return response

    file_object = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    res = requests.get(file_object.file_path)
    data = res.content
    # 文件分块处理（适用于大文件）     @孙歆尧
    # data = res.iter_content()

    # 设置content_type=application/octet-stream 用于提示下载框        @孙歆尧
    response = HttpResponse(data)
    # from django.utils.encoding import escape_uri_path

    response['Content-Disposition'] = "attachment; filename={};".format(file_object.name)
    # response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_object.name)
    return response
