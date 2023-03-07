import json

from django.shortcuts import redirect, render, HttpResponse
from random import sample
from untils.short_message import short_message
from untils.tencent.sms import send_sms_single


def sms_test(request):
    res = short_message(1876329931, 1714141)
    if res['result'] == 0:
        return HttpResponse('发送成功')
    return HttpResponse('发送失败' + res['errmsg'])
