import json
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection

from bug_manage import settings
from untils.encrypt import uid
from web import models
from untils.alipay import AliPay


def index(request):
    return render(request, 'index.html')


def price(request):
    policy_list = models.PricePolicy.objects.filter(category=2).all()
    return render(request, 'price.html', {'policy_list': policy_list})


def payment(request, policy_id):
    policy_obj = models.PricePolicy.objects.filter(id=policy_id, category=2).first()
    if not policy_obj:
        return redirect('price')
    number = request.GET.get('number', '')
    if not number or not number.isdecimal():
        return redirect('price')
    number = int(number)
    if number < 1:
        return redirect('price')
    # 原价
    origin_price = number * policy_obj.price
    balance = 0
    if request.tracer.price_policy.category == 2:
        _object = models.Transaction.objects.filter(user=request.tracer.user, price_policy__category=2,
                                                    end_time__gte=datetime.now()).order_by('-price_policy').first()
        if _object:
            total_timedalta = _object.end_time - _object.start_time
            balance_timedalta = _object.end_time - datetime.now()
            if total_timedalta == balance_timedalta:
                balance = (balance_timedalta.days - 1 / total_timedalta.days) * float(_object.actual_payment)
            else:
                balance = (balance_timedalta.days / total_timedalta.days) * float(_object.actual_payment)
        if balance >= origin_price:
            return redirect('price')
        context = {
            'policy_id': policy_obj.id,
            'number': number,
            'origin_price': origin_price,
            'balance': round(balance, 2),
            'total_price': origin_price - round(balance, 2)
        }
        conn = get_redis_connection()
        key = 'payment_{}'.format(request.tracer.user.mobile_phone)
        conn.set(key, json.dumps(context), ex=60 * 30)
        context['policy_object'] = policy_obj
        context['transaction'] = _object
        return render(request, 'payment.html', context)


def pay(request):
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    context_string = conn.get(key)
    if not context_string:
        return redirect('price')
    context = json.loads(context_string.decode('utf-8'))
    order_id = uid(request.tracer.user.mobile_phone)
    total_price = context['total_price']
    models.Transaction.objects.create(
        status=1,
        order=order_id,
        user=request.tracer.user,
        price_policy_id=context['policy_id'],
        count=context['number'],
        actual_payment=total_price
    )
    # 跳转到支付宝支付
    params = {
        'app_id': settings.ALIPAY_APPID,
        'method': 'alipay.trade.page.pay',
        'format': 'JSON',
        'return_url': "http://127.0.0.1:8000/pay/notify/",
        'notify_url': "http://127.0.0.1:8000/pay/return/",
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'version': '1.0',
        'biz_content': json.dumps({
            'out_trade_no': order_id,
            'product_code': 'FAST_INSTANT_TRADE_PAY',
            'total_amount': total_price,
            'subject': "tracer payment"
        }, separators=(',', ':'))
    }
    # 获取待签名的字符串
    unsigned_string = "&".join(["{0}={1}".format(k, params[k]) for k in sorted(params)])

    # 签名 SHA256WithRSA(对应sign_type为RSA2)
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from base64 import decodebytes, encodebytes

    # SHA256WithRSA + 应用私钥 对待签名的字符串 进行签名
    private_key = RSA.importKey(open("files/应用私匙.txt").read())
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(SHA256.new(unsigned_string.encode('utf-8')))

    # 对签名之后的执行进行base64 编码，转换为字符串
    sign_string = encodebytes(signature).decode("utf8").replace('\n', '')

    # 把生成的签名赋值给sign参数，拼接到请求参数中。

    from urllib.parse import quote_plus
    result = "&".join(["{0}={1}".format(k, quote_plus(params[k])) for k in sorted(params)])
    result = result + "&sign=" + quote_plus(sign_string)

    gateway = "https://openapi.alipaydev.com/gateway.do"
    ali_pay_url = "{}?{}".format(gateway, result)

    return redirect(ali_pay_url)


def pay_notify(request):
    ali_pay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url="http://127.0.0.1:8000/pay/notify/",
        return_url="http://127.0.0.1:8000/pay/notify/",
        app_private_key_path=settings.ALI_PRI_KEY_PATH,
        alipay_public_key_path=settings.ALI_PUB_KEY_PATH
    )
    if request.method == 'GET':
        # 只做跳转，判断是否支付成功了，不做订单的状态更新。
        # 支付吧会讲订单号返回：获取订单ID，然后根据订单ID做状态更新 + 认证。
        # 支付宝公钥对支付给我返回的数据request.GET 进行检查，通过则表示这是支付宝返还的接口。
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = ali_pay.verify(params, sign)
        if status:
            """
            current_datetime = datetime.datetime.now()
            out_trade_no = params['out_trade_no']
            _object = models.Transaction.objects.filter(order=out_trade_no).first()
    
            _object.status = 2
            _object.start_datetime = current_datetime
            _object.end_datetime = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            """
            return HttpResponse('支付完成')
        return HttpResponse('支付失败')

    else:
        from urllib.parse import parse_qs

    body_str = request.body.decode('utf-8')
    post_data = parse_qs(body_str)
    post_dict = {}
    for k, v in post_data.items():
        post_dict[k] = v[0]

    sign = post_dict.pop('sign', None)
    status = ali_pay.verify(post_dict, sign)
    if status:
        current_datetime = datetime.datetime.now()
        out_trade_no = post_dict['out_trade_no']
        _object = models.Transaction.objects.filter(order=out_trade_no).first()

        _object.status = 2
        _object.start_datetime = current_datetime
        _object.end_datetime = current_datetime + datetime.timedelta(days=365 * _object.count)
        _object.save()
        return HttpResponse('success')

    return HttpResponse('error')
