from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django import forms
from django_redis import get_redis_connection
from untils.bootstrap import BootStrapModelForm, BootStrapForm
from web import models
from untils.encrypt import getMD5


class UserInfoForm(BootStrapModelForm):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(regex=r'^(1[3|4|5|6|7|8|9])\d{9}$',
                                                                              message='手机号码格式错误')])
    password = forms.CharField(label='密码', min_length=8, max_length=64,
                               error_messages={'min_length': "密码长度不能小于8个字符",
                                               'max_length': "密码长度不能大于64个字符"}, widget=forms.PasswordInput())
    password_conf = forms.CharField(label='重复密码', min_length=8, max_length=64,
                                    error_messages={'min_length': "密码长度不能小于8个字符",
                                                    'max_length': "密码长度不能大于64个字符"},
                                    widget=forms.PasswordInput())
    code = forms.CharField(label='验证码')

    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'password_conf', 'mobile_phone', 'code']

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return getMD5(pwd)

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已经存在')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已经存在')
        return username

    def clean_password_conf(self):
        password_conf = self.cleaned_data['password_conf']
        password = self.cleaned_data['password']
        if getMD5(password_conf) != password:
            raise ValidationError('两次输入的密码不一致')
        return password_conf

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已经存在')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        redis_conn = get_redis_connection()
        if not mobile_phone:
            return code
        redis_code = redis_conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')
        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误，请重新输入')
        return code


class LoginForm(BootStrapForm):
    username = forms.CharField(label='手机号或邮箱')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')


class LoginSMSForm(BootStrapForm):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(regex=r'^(1[3|4|5|6|7|8|9])\d{9}$',
                                                                              message='手机号码格式错误')])
    code = forms.CharField(label='验证码')
