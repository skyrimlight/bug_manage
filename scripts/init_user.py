import django
import os
import sys

"""获取当前文件路径，将当前目录添加到系统默认目录中"""
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

"""读取django的默认配置"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bug_manage.settings")
django.setup()
"""操作数据库"""
from web import models


def run():
    exists = models.UserInfo.objects.filter(username='休琴忘谱').exists()
    if not exists:
        models.UserInfo.objects.create(username='休琴忘谱', email='xxxxxx@gmail.com', mobile_phone='13258962007',
                                       password='eba2b65ead3ec884d2fbe057703c3323')


if __name__ == '__main__':
    run()
