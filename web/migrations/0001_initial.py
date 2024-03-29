# Generated by Django 4.1.7 on 2023-02-27 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=32, verbose_name="用户名")),
                ("password", models.CharField(max_length=32, verbose_name="密码")),
                ("email", models.EmailField(max_length=32, verbose_name="邮箱")),
                ("mobile_phone", models.CharField(max_length=11, verbose_name="手机号")),
            ],
        ),
    ]
