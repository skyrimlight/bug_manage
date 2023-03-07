import hashlib
import uuid
from time import time

from django.conf import settings


def getMD5(data_string):
    # settings.SECRET_KEY为django随机生成的字符串
    obj = hashlib.md5(settings.SECRET_KEY.encode(encoding='utf-8'))
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()


def uid(string):
    data = "{}-{}".format(str(int(time() * 1000)), string)
    return data
