from random import sample

from untils.tencent.sms import send_sms_single


def short_message(phone, template_id):
    """

    :param phone: 手机号
    :param template_id:模板id， 重置密码1714143，用户登录1714142，用户注册1714141
    :return:
    """
    nums_str = '0123456789' * 6
    code_list = sample(nums_str, 6)
    code_str = "".join(code_list)
    res = send_sms_single(phone, template_id, [code_str, ])
    if res['result'] == 0:
        return {'result': 0, 'code': code_str}
    return {'result': res['result'], 'errmsg': res['errmsg']}
