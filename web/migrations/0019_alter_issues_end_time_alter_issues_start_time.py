# Generated by Django 4.1.7 on 2023-03-04 13:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0018_rename_model_module"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issues",
            name="end_time",
            field=models.DateField(blank=True, null=True, verbose_name="截止日期"),
        ),
        migrations.AlterField(
            model_name="issues",
            name="start_time",
            field=models.DateField(blank=True, null=True, verbose_name="开始时间"),
        ),
    ]
