import time
import datetime
import collections

from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count

from web import models


def dashboard(request, project_id):
    """概览"""
    status_dict = collections.OrderedDict()  # 有序字典
    for key, text in models.Issues.status_choices:
        status_dict[key] = {'text': text, 'count': 0}
    # 根据id来分别统计问题的数量
    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    # 项目成员
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values('user_id', 'user__username')

    # 最近的10个问题
    # top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]

    # data_list = models.Issues.status_choices
    # print(data_list)
    # # ((1, '新建'), (2, '处理中'), (3, '已解决'), (4, '已忽略'), (5, '待反馈'), (6, '已关闭'), (7, '重新打开'))
    # status_dict = {}
    # for i in data_list:
    #     dict_item_text = {}
    #     dict_item_text['count'] = models.Issues.objects.filter(status=i[0]).count()
    #     dict_item_text['text'] = i[1]
    #     status_dict[i[0]] = dict_item_text
    top_ten_object = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by(
        '-create_datetime')[0:10]
    user_list = models.ProjectUser.objects.filter(project_id=project_id).all()

    return render(request, 'dashboard.html',
                  {'status_dict': status_dict, 'top_ten_object': top_ten_object, 'user_list': user_list})


# def issues_chart(request, project_id):
#     today = datetime.datetime.now().date()
#     date_dict = collections.OrderedDict()
#     for i in range(0, 30):
#         date = today - datetime.timedelta(days=i)
#         date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]
#
#     # "DATE_FORMAT(web_transaction.create_datetime,'%%Y-%%m-%%d')"
#     result = models.Issues.objects.filter(project_id=project_id,
#                                           create_datetime__gte=today - datetime.timedelta(
#                                               days=30)).extra(
#         select={'ctime': "DATE_FORMAT(web_transaction.create_time,'%%Y-%%m-%%d')"}).values('ctime').annotate(
#         ct=Count('id'))
#     for item in result:
#         date_dict[item['ctime']][1] = item['ct']
#     print(result)
#     return JsonResponse({'status': True, 'data': list(date_dict.values())})


def issues_chart(request, project_id):
    """ 在概览页面生成highcharts所需的数据 """
    today = datetime.datetime.now().date()
    date_dict = collections.OrderedDict()
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)
        date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

    # print(date_dict)
    # OrderedDict([('2023-03-06', [1678032000000.0, 0]), ('2023-03-05', [1677945600000.0, 0]),
    #              ('2023-02-06', [1675612800000.0, 0]), ('2023-02-05', [1675526400000.0, 0])])

    # "DATE_FORMAT(web_transaction.create_datetime,'%%Y-%%m-%%d')"
    # result = models.Issues.objects.filter(project_id=project_id,
    #                                       create_datetime__gte=today - datetime.timedelta(days=30)).extra(
    #     select={'ctime': "DATE_FORMAT(web_transaction.create_datetime,'%%Y-%%m-%%d')"}).values('ctime').annotate(ct=Count('id'))
    #
    # for item in result:
    #     date_dict[item['ctime']][1] = item['ct']
    # for i in date_dict:
    #     models.Issues.objects.filter(project_id=project_id,
    #                                       create_datetime__gte=today - datetime.timedelta(days=30))
    # 根据自己写的sql执行
    print(date_dict)
    with connection.cursor() as cursor:
        # 执行sql语句
        result = cursor.execute(f"""
        SELECT count(id),DATE_FORMAT(CREATE_DATETIME,'%Y-%m-%d') as datetime from web_issues WHERE PROJECT_ID = {request.tracer.project.id} AND  CREATE_DATETIME > DATE_SUB(NOW(),INTERVAL 1 MONTH) GROUP BY datetime
        """)
        # 查出一条数据
        # row = cursor.fetchone()
        # 查出所有数据
        row = cursor.fetchall()
    for i in row:
        date_dict[i[1]][1] = i[0]

    return JsonResponse({'status': True, 'data': list(date_dict.values())})
