import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from untils.encrypt import uid
from untils.pagination import Pagination
from web import models
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm
from web.forms.invite import InviteModelForm


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成URL
            # 在当前URL的基础上去增加一项
            # status=1&age=19
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")


def issues(request, project_id):
    """
    展示问题页面以及添加问题
    :param request:
    :param project_id:
    :return:
    """
    if request.method == 'GET':
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        conditions = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)
            if not value_list:
                continue
            conditions[f'{name}__in'] = value_list
        queryset = models.Issues.objects.filter(project=request.tracer.project).filter(**conditions)
        # issues_object_list = models.Issues.objects.filter(project=request.tracer.project).all()
        page_object = Pagination(request, queryset, page_size=2)
        form = IssuesModelForm(request)
        project_issues_type = models.IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')

        project_total_user = [(request.tracer.project.creator_id, request.tracer.project.creator.username,)]
        join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')
        project_total_user.extend(join_user)
        invite_form = InviteModelForm()
        context = {
            'form': form,
            # 'issues_object_list': queryset,
            'filter_list': [
                {'title': "问题类型", 'filter': CheckFilter('issues_type', project_issues_type, request)},
                {'title': "状态", 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': "优先级", 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': "指派者", 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': "关注者", 'filter': SelectFilter('attention', project_total_user, request)},
            ],
            "issues_object_list": page_object.page_queryset,  # 分完页的数据
            "page_string": page_object.html(),  # 页码
            'invite_form': invite_form
        }
        return render(request, 'issues.html', context)
    form = IssuesModelForm(request, request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.instance.project = request.tracer.project
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': True, 'errors': form.errors})


def issues_detail(request, project_id, issues_id):
    issues_info = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    form = IssuesModelForm(request, instance=issues_info)
    # print(form)
    return render(request, 'issues_detail.html', {'form': form, 'issues_info': issues_info})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    if request.method == 'GET':
        record_list = models.IssuesReply.objects.filter(issues_id=issues_id).all()
        data_list = []

        for row in record_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                "creator": row.creator.username,
                'datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                'parent_id': row.reply_id
            }
            data_list.append(data)
        # print(data_list)
        return JsonResponse({'status': True, 'data': data_list})
    form = IssuesReplyModelForm(request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.creator = request.tracer.user
        form.instance.reply_type = 2
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    issues_obj = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode('utf-8'))
    name = post_dict.get('name')
    value = post_dict.get('value')
    field_obj = models.Issues._meta.get_field(name)

    # 常用方法封装
    def create_reply_record(content):
        new_obj = models.IssuesReply.objects.create(reply_type=1, issues=issues_obj, content=msg,
                                                    creator=request.tracer.user)

        new_reply_dict = {
            'id': new_obj.id,
            'reply_type': new_obj.get_reply_type_display(),
            'creator': new_obj.creator.username,
            'content': new_obj.content,
            'datetime': new_obj.create_datetime,
            'parent_id': new_obj.reply_id
        }
        return new_reply_dict

    if name in ['subject', 'desc', 'start_time', 'end_time']:
        if not value:
            if field_obj.null:
                setattr(issues_obj, name, None)
                issues_obj.save()
                msg = f'字段{field_obj.verbose_name}变更为空'
            else:
                return JsonResponse({'status': False, 'error': '字段不能为空'})
        else:
            setattr(issues_obj, name, value)
            issues_obj.save()
            msg = f'字段{field_obj.verbose_name}变更为{value}'
        return JsonResponse({'status': True, 'data': create_reply_record(msg)})
    elif name in ['issues_type', 'assign', 'module', 'parent']:
        if not value:
            if field_obj.null:
                setattr(issues_obj, name, None)
                issues_obj.save()
                msg = f'字段{field_obj.verbose_name}变更为空'
            else:
                return JsonResponse({'status': False, 'error': '字段不能为空'})
        else:
            if name == 'assign':
                # 处理人需要判断是否是创建者或者参与者
                if value == str(request.tracer.project.creator_id):
                    instance = request.tracer.project.creator
                else:
                    project_user_info = models.ProjectUser.objects.filter(project_id=project_id, user_id=value).first()
                    if project_user_info:
                        instance = project_user_info.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': '值不存在'})
                setattr(issues_obj, name, instance)
                issues_obj.save()
                msg = f'字段{field_obj.verbose_name}变更为{str(instance)}'
                # 判断用户是否是规定输入的值remote_field
            else:
                instance = field_obj.remote_field.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': '值不存在'})
                setattr(issues_obj, name, instance)
                issues_obj.save()
                msg = f'字段{field_obj.verbose_name}变更为{str(instance)}'

        return JsonResponse({'status': True, 'data': create_reply_record(msg)})
    elif name in ['priority_level', 'mode', 'status']:
        selected_text = None
        print(field_obj.choices)
        for key, text in field_obj.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': '值不存在'})
        setattr(issues_obj, name, value)
        issues_obj.save()
        msg = f'{field_obj.verbose_name}更新为{selected_text}'
        return JsonResponse({'status': True, 'data': create_reply_record(msg)})
    if name == "attention":
        # {"name":"attention","value":[1,2,3]}
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': "数据格式错误"})

        if not value:
            issues_obj.attention.set(value)
            issues_obj.save()
            msg = "{}更新为空".format(field_obj.verbose_name)
        else:
            # values=["1","2,3,4]  ->   id是否是项目成员（参与者、创建者）
            # 获取当前项目的所有成员
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在请重新设置"})
                username_list.append(username)

            issues_obj.attention.set(value)
            issues_obj.save()
            msg = "{}更新为{}".format(field_obj.verbose_name, ",".join(username_list))

        return JsonResponse({'status': True, 'data': create_reply_record(msg)})

    return JsonResponse({'status': False, 'error': "滚"})


def invite_url(request, project_id):
    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        # return JsonResponse({'status': True, 'data': '生成邀请码失败'})
        if request.tracer.project.creator != request.tracer.user:
            form.add_error('period', '无权创建邀请码')
            return JsonResponse({'status': False, 'error': form.errors})
        invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.project = request.tracer.project
        form.instance.code = invite_code
        form.instance.creator = request.tracer.user
        form.save()
        url_path = reverse('invite_join', kwargs={'code': invite_code})
        url = f'{request.scheme}://{request.get_host()}{url_path}'

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    invite_obj = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_obj:
        return render(request, 'invite_join.html', {'error': '邀请码不存在'})
    if invite_obj.creator == request.tracer.user:
        return redirect('project_list')
    has_join = models.ProjectUser.objects.filter(project=invite_obj.project, user=request.tracer.user).exists()
    if has_join:
        return redirect('project_list')
    member = models.ProjectUser.objects.filter(project=invite_obj.project).count()
    # 邀请码开始时间
    current_datetime = invite_obj.create_datetime
    limit_datetime = current_datetime + timedelta(minutes=invite_obj.period)
    datetime_now = datetime.now()
    # print(limit_datetime)
    # print(datetime_now)
    # limit_datetime = limit_datetime.replace(tzinfo=None)
    if limit_datetime < datetime_now:
        return render(request, 'invite_join.html', {'error': '邀请码已过期'})

    if request.tracer.price_policy.project_member <= member:
        return render(request, 'invite_join.html', {'error': '项目已满员'})

    if invite_obj.count:
        if invite_obj.count - invite_obj.use_count <= 0:
            return render(request, 'invite_join.html', {'error': '邀请人数已满'})
    elif request.tracer.price_policy.project_member > member:
        models.ProjectUser.objects.create(project=invite_obj.project, user=request.tracer.user)
        invite_obj.use_count += 1
        request.tracer.price_policy.project_member += 1
        invite_obj.save()
        request.tracer.price_policy.save()
        return render(request, 'invite_join.html')
