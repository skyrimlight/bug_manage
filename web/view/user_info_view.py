import re
import uuid
from datetime import datetime
from io import BytesIO

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django_redis import get_redis_connection

from bug_manage.settings import TENCENT_SMS_TEMPLATE
from untils.code import check_code
from untils.short_message import short_message
from web import models
from web.forms.userinfo import UserInfoForm, LoginForm, LoginSMSForm
from untils.encrypt import getMD5


# redis使用方法之一
# pool = redis.ConnectionPool(host='localhost', port=6379, db=2, encoding='utf-8', decode_responses=True,
#                             password='skyrimlight', max_connections=1000)
# redis_conn = redis.Redis(connection_pool=pool)


def user_register(request):
    """注册"""
    if request.method == 'GET':
        form = UserInfoForm()
        return render(request, 'register.html', {'form': form})
    form = UserInfoForm(data=request.POST)
    if form.is_valid():
        redis_conn = get_redis_connection()
        local_code = redis_conn.get(form.cleaned_data['mobile_phone'])
        code = request.POST.get('code')
        local_code = str(local_code, 'utf-8')
        if code == local_code:
            instance = form.save()
            policy_object = models.PricePolicy.objects.filter(category=1, title="个人免费版").first()
            models.Transaction.objects.create(status=2, user=instance, price_policy=policy_object, actual_payment=0,
                                              count=0, order=str(uuid.uuid4()), start_time=datetime.now()
                                              )
            return JsonResponse({'status': True, 'data': '/login/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})
    return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    """发送验证码"""
    sms_template = request.GET.get('tpl')
    print(sms_template)
    mobile_phone = request.GET.get('mobile_phone')
    phone_num = re.match(string=mobile_phone, pattern=r'^(1[3|4|5|6|7|8|9])\d{9}$')
    if not phone_num:
        return JsonResponse({'status': False, 'error': '手机号格式不正确'})
    phone = phone_num.group()
    if sms_template == 'register':
        """注册发送验证码"""
        phone_info = models.UserInfo.objects.filter(mobile_phone=phone_num).first()
        if phone_info:
            return JsonResponse({'status': False, 'error': '此手机号已经注册'})
    elif sms_template == 'login':
        """登录发送验证码"""
        phone_info = models.UserInfo.objects.filter(mobile_phone=phone).first()
        if not phone_info:
            return JsonResponse({'status': False, 'error': '此手机号未注册'})
    else:
        """重置密码验证码"""
        pass
    result = short_message(phone, TENCENT_SMS_TEMPLATE[sms_template])
    if result['result'] == 0:
        redis_conn = get_redis_connection()
        redis_conn.set(name=mobile_phone, value=result['code'], ex=3000)
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': result['errmsg']})


def user_login(request):
    """通过用户手机号或邮箱"""
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    form = LoginForm(data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = getMD5(form.cleaned_data['password'])
        code = form.cleaned_data['code']
        image_code = request.session.get('image_code')
        if code.strip().upper() != image_code:
            form.add_error('code', '验证码输入错误或已过期')
            return render(request, 'login.html', {'form': form})
        user_info = models.UserInfo.objects.filter(Q(email=username) | Q(mobile_phone=username)).filter(
            password=password).first()
        if user_info:
            request.session['user_id'] = user_info.id
            request.session.set_expiry(60 * 60 * 24 * 14)
            return redirect('index')
    return render(request, 'login.html', {'form': form})


def image_code(request):
    """验证码生成"""
    img, code_string = check_code()
    # 将生成验证码的文本信息写入到session中，以便后续校验验证码
    request.session["image_code"] = code_string
    # 设置session有效时间为60s
    request.session.set_expiry(60)
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def user_login_by_sms(request):
    """通过手机验证码登录"""
    if request.method == 'GET':
        form = LoginSMSForm()
        return render(request, 'login_sms.html', {'form': form})
    form = LoginSMSForm(data=request.POST)
    if form.is_valid():
        mobile_phone = form.cleaned_data['mobile_phone']
        code = form.cleaned_data['code']
        redis_conn = get_redis_connection()
        local_code = redis_conn.get(mobile_phone)
        local_code = str(local_code, 'utf-8')
        if code == local_code:
            user_obj = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
            request.session['user_id'] = user_obj.id
            request.session.set_expiry(60 * 60 * 24 * 14)
            return JsonResponse({"status": True, 'data': "/index/"})
    return JsonResponse({"status": False, 'error': form.errors})


def logout(request):
    request.session.clear()
    # request.session.flush()
    return redirect('index')
