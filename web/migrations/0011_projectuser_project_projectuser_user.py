# Generated by Django 4.1.7 on 2023-02-28 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0010_remove_projectuser_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectuser",
            name="project",
            field=models.ForeignKey(
                default=9,
                on_delete=django.db.models.deletion.CASCADE,
                to="web.project",
                verbose_name="项目",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="projectuser",
            name="user",
            field=models.ForeignKey(
                default=9,
                on_delete=django.db.models.deletion.CASCADE,
                to="web.userinfo",
                verbose_name="用户",
            ),
            preserve_default=False,
        ),
    ]