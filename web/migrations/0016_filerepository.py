# Generated by Django 4.1.7 on 2023-03-02 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0015_project_bucket_project_region"),
    ]

    operations = [
        migrations.CreateModel(
            name="FileRepository",
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
                (
                    "name",
                    models.CharField(
                        help_text="文件/文件夹名", max_length=32, verbose_name="文件夹名称"
                    ),
                ),
                ("file_type", models.BooleanField(verbose_name="类型")),
                (
                    "file_size",
                    models.IntegerField(
                        blank=True, help_text="字节", null=True, verbose_name="大小"
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="cos文件名"
                    ),
                ),
                (
                    "file_path",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="文件路径"
                    ),
                ),
                (
                    "update_datetime",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="child",
                        to="web.filerepository",
                        verbose_name="父目录",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="web.project",
                        verbose_name="项目id",
                    ),
                ),
                (
                    "update_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="web.userinfo",
                        verbose_name="最近更新者",
                    ),
                ),
            ],
        ),
    ]