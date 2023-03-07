import collections

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from web import models


def statistics(request, project_id):
    # data_dict = {}
    # for key, value in models.Issues.priority_choices:
    #     data_dict[key] = {'name': value, 'y': 0}
    #
    # start_time = request.GET.get('start')
    # end_time = request.GET.get('end')
    # # [{'priority_level': 'info', 'count': 4}, {'priority_level': 'warning', 'count': 1}] >
    # dict_info = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start_time,
    #                                          create_datetime__lt=end_time).values('priority_level').annotate(
    #     count=Count('id'))
    # for i in dict_info:
    #     data_dict[i['priority_level']]['y'] = i['count']

    return render(request, 'statistics.html')


def statistics_priority(request, project_id):
    data_dict = {}
    for key, value in models.Issues.priority_choices:
        data_dict[key] = {'name': value, 'y': 0}

    start_time = request.GET.get('start')
    end_time = request.GET.get('end')
    # [{'priority_level': 'info', 'count': 4}, {'priority_level': 'warning', 'count': 1}] >
    dict_info = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start_time,
                                             create_datetime__lt=end_time).values('priority_level').annotate(
        count=Count('id'))
    for i in dict_info:
        data_dict[i['priority_level']]['y'] = i['count']
    return JsonResponse({'status': True, 'data': list(data_dict.values())})


def statistics_project_user(request, project_id):
    start_time = '2023-03-01'
    end_time = '2023-03-09'
    result_user = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start_time,
                                               create_datetime__lt=end_time, assign__isnull=False).order_by(
        'assign_id', 'status').values_list('assign__username', 'status').annotate(ct=Count('id'))
    # < QuerySet[('休琴忘谱', 2, 1), ('skyrimlight', 1, 1), ('无常元帅', 1, 1), ('无常元帅', 4, 1)] >
    # < QuerySet[ < Issues: 选择一个有效的选项。 warning
    # 不在可用的选项中。 >, < Issues: JsonResponse >, < Issues: 重置密码功能 >, < Issues: 测试 >] >
    categories = []
    data = []
    for i in result_user:
        if i[0] not in categories:
            categories.append(i[0])

    for i in models.Issues.status_choices:
        data.append({'name': i[1], 'data': [0] * (len(categories) + 1)})

    for i in result_user:
        data[i[1] - 1]['data'][categories.index(i[0])] = i[2]
    not_assign = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start_time,
                                              create_datetime__lt=end_time, assign__isnull=True).count()
    data[0]['data'][-1] = not_assign
    categories.append('未指派')
    context = {
        'status': True,
        'data': {
            'categories': categories,
            'series': data
        }
    }
    # start = request.GET.get('start')
    # end = request.GET.get('end')
    # all_user_dict = collections.OrderedDict()
    # all_user_dict[request.tracer.project.creator.id] = {
    #     'name': request.tracer.project.creator.username,
    #     'status': {item[0]: 0 for item in models.Issues.status_choices}
    # }
    # all_user_dict[None] = {
    #     'name': '未指派',
    #     'status': {item[0]: 0 for item in models.Issues.status_choices}
    # }
    # user_list = models.ProjectUser.objects.filter(project_id=project_id)
    # for item in user_list:
    #     all_user_dict[item.user_id] = {
    #         'name': item.user.username,
    #         'status': {item[0]: 0 for item in models.Issues.status_choices}
    #     }
    #
    # # 2. 去数据库获取相关的所有问题
    # issues = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start, create_datetime__lt=end)
    # for item in issues:
    #     if not item.assign:
    #         all_user_dict[None]['status'][item.status] += 1
    #     else:
    #         all_user_dict[item.assign_id]['status'][item.status] += 1
    #
    # # 3.获取所有的成员
    # categories = [data['name'] for data in all_user_dict.values()]
    #
    # # 4.构造字典
    # """
    # data_result_dict = {
    #     1:{name:新建,data:[1，2，3，4]},
    #     2:{name:处理中,data:[3，4，5]},
    #     3:{name:已解决,data:[]},
    #     4:{name:已忽略,data:[]},
    #     5:{name:待反馈,data:[]},
    #     6:{name:已关闭,data:[]},
    #     7:{name:重新打开,data:[]},
    # }
    # """
    # data_result_dict = collections.OrderedDict()
    # for item in models.Issues.status_choices:
    #     data_result_dict[item[0]] = {'name': item[1], "data": []}
    #
    # for key, text in models.Issues.status_choices:
    #     # key=1,text='新建'
    #     for row in all_user_dict.values():
    #         count = row['status'][key]
    #         data_result_dict[key]['data'].append(count)
    # print(categories)
    # print(data_result_dict)
    # context = {
    #     'status': True,
    #     'data': {
    #         'categories': categories,
    #         'series': list(data_result_dict.values())
    #     }
    # }
    return JsonResponse(context)
