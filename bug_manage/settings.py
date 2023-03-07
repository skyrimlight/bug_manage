"""
Django settings for bug_manage project.

Generated by 'django-admin startproject' using Django 4.2a1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-!3k_5%^v6g%((bn)1%zkl9*&_octkcb55_g5sw^6hw9zvl-bl9"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "web.apps.WebConfig"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "web.middlewares.auth.AuthMiddleware"
]

ROOT_URLCONF = "bug_manage.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')]
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bug_manage.wsgi.application"

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

TENCENT_SMS_TEMPLATE = {
    'register': 1714141,
    'login': 1714142,
    'reset': 1714143
}
ALIPAY_APPID = ''
ALI_PRI_KEY_PATH = ''
ALI_PUB_KEY_PATH = ''
try:
    from .local_settings import *
except Exception:
    # appid
    TENCENT_SMS_APP_ID = ''
    # appkey
    TENCENT_SMS_APP_KEY = ''
    # sms_sign
    TENCENT_SMS_SIGN = ''

    COS_SECRET_ID = ''
    COS_SECRET_KEY = ''
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'django',
            'USER': 'skyrimlight',
            'PASSWORD': 'skyrimlight',
            'HOST': '127.0.0.1',
            'PORT': 3306
        }
    }
# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
X_FRAME_OPTIONS = 'SAMEORIGIN'  # 表示该页面可以在相同域名页面的frame中展示。
LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = "static/"
# 白名单，允许不经登录访问的页面
WHITE_REGEX_URL_LIST = [
    "/register/",
    "/send/sms/",
    "/send_sms/",
    "/login/",
    "/login/sms/",
    "/image/code/",
    "/image_code/",
    "/index/",
    "/price/",
]

# Default primary key field type
# https://docs.djangoproject.com/en/dev/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"