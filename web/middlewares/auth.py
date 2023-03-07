from datetime import datetime

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

from web import models
from bug_manage.settings import WHITE_REGEX_URL_LIST


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.tracer = Tracer()
        user_id = request.session.get('user_id')
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        request.tracer.user = user_obj
        # 白名单验证，访问的路径在白名单里放行，不在验证是否登录
        path = request.path
        if path in WHITE_REGEX_URL_LIST:
            return
        # 检查用户是否登录，未登录返回登陆页面

        if not request.tracer.user:
            return redirect('login')
        # 获取用户的空间额度
        # 方式一
        _object = models.Transaction.objects.filter(user=user_obj, end_time__gte=datetime.now()).order_by(
            '-price_policy').first()
        if not _object:
            _object = models.Transaction.objects.filter(user=user_obj, price_policy=1).first()
        # request.transaction = _object
        request.tracer.price_policy = _object.price_policy

    def process_view(self, request, view, args, kwargs):
        # path = request.path.split('/')
        # print(path)
        # 判断url是否以manage开头，如果是则判断项目ID是否是我创建
        if not request.path.startswith('/manage/'):
            return
        project_id = kwargs.get('project_id')
        if project_id:
            object = models.Project.objects.filter(id=project_id, creator=request.tracer.user).first()
            if object:
                request.tracer.project = object
                return
            user_object = models.ProjectUser.objects.filter(project=project_id, user=request.tracer.user).first()
            if user_object:
                request.tracer.project = user_object
                return
        return redirect('project_list')
