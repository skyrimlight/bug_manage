import uuid

from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from untils.encrypt import uid
from untils.tencent.cos import upload_file
from web import models
from web.forms.wiki import WikiModelForm


def wiki(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id:
        return render(request, 'wiki.html')
    if not wiki_id.isdecimal():
        return render(request, 'wiki.html')
    if wiki_id:
        wiki_obj = models.Wiki.objects.filter(id=wiki_id, project=project_id).first()
        return render(request, 'wiki.html', {'wiki_obj': wiki_obj})
    return render(request, 'wiki.html')


def wiki_add(request, project_id):
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_form.html', {'form': form})
    form = WikiModelForm(request, request.POST)
    # print(form)
    if form.is_valid():
        form.instance.project = request.tracer.project
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    return render(request, 'wiki_form.html', {'form': form})


def wiki_catalog(request, project_id):
    # values_list返回和一个数组，values返回一个字典
    data = models.Wiki.objects.filter(project=project_id).all().values('id', 'title', 'parent_id').order_by('depth',
                                                                                                            'id')
    return JsonResponse({'status': True, 'data': list(data)})


# def wiki_detail(request, project_id, wiki_id):
#     pass


def wiki_edit(request, project_id, wiki_id):
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project=project_id).first()
    if not wiki_obj:
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    if request.method == 'GET':
        form = WikiModelForm(request, instance=wiki_obj)
        return render(request, 'wiki_form.html', {"form": form})
    form = WikiModelForm(request, data=request.POST, instance=wiki_obj)
    if form.is_valid():
        form.save()
    url = reverse('wiki', kwargs={'project_id': project_id})
    preview_url = f'{url}?wiki_id={wiki_id}'
    return redirect(preview_url)


def wiki_delete(request, project_id, wiki_id):
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project=project_id).first()
    wiki_obj.delete()
    url = reverse('wiki', kwargs={'project_id': project_id})
    return redirect(url)


@csrf_exempt
def wiki_upload(request, project_id):
    result = {
        'success': 0, 'message': None, 'url': None
    }
    image_obj = request.FILES.get('editormd-image-file')
    if not image_obj:
        result['message'] = '文件不存在'
        return JsonResponse(result)
    ext = image_obj.name.rsplit('.')[-1]
    key = f'{uid(request.tracer.user.id)}.{ext}'
    img_url = upload_file(bucket_path=request.tracer.project.bucket,
                          file_path=image_obj,
                          filename=key,
                          region=request.tracer.project.region
                          )
    result['success'] = 1
    result['url'] = img_url
    # https: // xiaoyaoyou - 1302221415.    cos.ap - nanjing.myqcloud.com / picture.jpg
    return JsonResponse(result)
