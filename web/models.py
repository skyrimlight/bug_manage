from django.db import models


# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32, db_index=True)
    password = models.CharField(verbose_name='密码', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    mobile_phone = models.CharField(verbose_name='手机号', max_length=11)

    def __str__(self):
        return self.username


class PricePolicy(models.Model):
    """价格策略"""
    category_choices = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )
    category = models.SmallIntegerField(verbose_name='收费类型', choices=category_choices, default=1)
    title = models.CharField(verbose_name='标题', max_length=20)
    price = models.PositiveIntegerField(verbose_name='价格')  # 正整数
    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员数', help_text='M')
    project_space = models.PositiveIntegerField(verbose_name='单个项目空间', help_text='M')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Transaction(models.Model):
    """订单记录"""
    status_choices = ((1, "待支付"), (2, "已支付"))
    status = models.SmallIntegerField(verbose_name='订单状态', choices=status_choices)
    user = models.ForeignKey(to='UserInfo', to_field='id', verbose_name='用户', on_delete=models.CASCADE)
    price_policy = models.ForeignKey(to='PricePolicy', to_field='id', verbose_name='价格策略', on_delete=models.CASCADE)
    actual_payment = models.DecimalField(verbose_name='实际支付价格', max_digits=12, decimal_places=2)
    start_time = models.DateTimeField(verbose_name="订单开始时间", null=True, blank=True)
    end_time = models.DateTimeField(verbose_name="订单结束时间", null=True, blank=True)
    count = models.IntegerField(verbose_name="购买数量(年)", help_text='0表示无限期')
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)
    create_time = models.DateField(verbose_name="订单创建时间", auto_now_add=True)


class Project(models.Model):
    """用户项目"""
    COLOR_CHOICES = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )
    name = models.CharField(verbose_name='项目名称', max_length=64)
    desc = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)
    color = models.SmallIntegerField(verbose_name='项目颜色', choices=COLOR_CHOICES, default=1)
    star = models.BooleanField(verbose_name='标星', default=False)
    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', to_field='id', on_delete=models.CASCADE)
    use_space = models.BigIntegerField(verbose_name='已用空间', default=0, help_text='字节')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(verbose_name='cos桶', max_length=128)
    region = models.CharField(verbose_name='cos区域', max_length=32)

    # 查询：可以省事；
    # 增加、删除、修改：无法完成
    # project_user = models.ManyToManyField(to='UserInfo',through="ProjectUser",through_fields=('project','user'))
    # def __repr__(self):
    #     return self.name


class ProjectUser(models.Model):
    """项目参与者"""

    project = models.ForeignKey(verbose_name='项目', to='Project', to_field='id', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='用户', to='UserInfo', to_field='id', on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标', default=False)
    create_time = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)


class Wiki(models.Model):
    title = models.CharField(verbose_name='标题', max_length=32)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='内容')
    depth = models.IntegerField(verbose_name='深度', default=1)
    # 子关联
    parent = models.ForeignKey(verbose_name='父文章', to="Wiki", null=True, blank=True, related_name='children',
                               on_delete=models.CASCADE)

    # def __repr__(self):
    #     return self.title

    def __str__(self):
        return self.title


class FileRepository(models.Model):
    """文件库"""
    project = models.ForeignKey(verbose_name='项目id', to='Project', on_delete=models.CASCADE)
    # file_type_choices = (
    #     (1, '文件'),
    #     (2, '文件夹')
    # )
    name = models.CharField(verbose_name='文件夹名称', max_length=32, help_text="文件/文件夹名")
    file_type = models.BooleanField(verbose_name='类型')
    # file_type = models.SmallIntegerField(verbose_name='类型', choices=file_type_choices)
    file_size = models.IntegerField(verbose_name='大小', null=True, blank=True, help_text='字节')
    parent = models.ForeignKey(verbose_name='父目录', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.CASCADE)
    key = models.CharField(verbose_name='cos文件名', max_length=128, null=True, blank=True)
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True,
                                 blank=True)  # https://桶.cos.ap-chengdu/....
    update_user = models.ForeignKey(verbose_name='最近更新者', to='UserInfo', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)


class Issues(models.Model):
    """问题"""
    subject = models.CharField(verbose_name='主题', max_length=32)
    desc = models.TextField(verbose_name='问题描述')
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    status_choices = (
        (1, '新建'), (2, '处理中'), (3, '已解决'), (4, '已忽略'), (5, '待反馈'), (6, '已关闭'), (7, '重新打开'))
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    priority_choices = (('info', '低'), ('warning', '中'), ('danger', '高'))
    priority_level = models.CharField(verbose_name='优先度', choices=priority_choices, max_length=12, default='info')
    assign = models.ForeignKey(verbose_name='处理人', to=UserInfo, related_name='task', null=True, blank=True,
                               on_delete=models.SET_NULL)
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.SET_NULL)
    attention = models.ManyToManyField(verbose_name='关注人', to='UserInfo', related_name='observe', blank=True)
    start_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='截止日期', null=True, blank=True)
    mode_choices = ((1, '公开模式'), (2, '隐私模式'))
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)
    parent = models.ForeignKey(verbose_name='关联问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_problems',
                                on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class IssuesType(models.Model):
    """问题类型"""
    PROJECT_INIT_LIST = ['任务', '功能', 'Bug']
    # question_choices = ((1, 'Bug'), (2, '功能'), (3, '任务'))
    # question_class = models.IntegerField(verbose_name='问题类型', choices=question_choices)
    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Module(models.Model):
    """模块"""
    # model_choice = (
    #     (1, '用户'), (2, '订单'), (3, '项目'), (4, 'wiki'), (5, '文件'), (6, '问题'), (7, '支付')
    # )
    # title = models.IntegerField(verbose_name='模块', choices=model_choice)
    title = models.CharField(verbose_name='模块', max_length=12)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class IssuesReply(models.Model):
    reply_type_choices = (
        (1, '修改记录'),
        (2, '回复')
    )
    reply_type = models.IntegerField(verbose_name='类型', choices=reply_type_choices)
    issues = models.ForeignKey(verbose_name='问题', to='Issues', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='评论内容')
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_reply',
                                on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    reply = models.ForeignKey(verbose_name='上级评论', to='self', null=True, blank=True, on_delete=models.CASCADE)


class ProjectInvite(models.Model):
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count = models.PositiveIntegerField(verbose_name='限制数量', null=True, blank=True, help_text='空表示无数量限制')
    use_count = models.PositiveIntegerField(verbose_name='已邀请数量', default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_invite',
                                on_delete=models.CASCADE)
