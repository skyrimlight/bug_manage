# Generated by Django 4.1.7 on 2023-03-01 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0012_wike"),
    ]

    operations = [
        migrations.CreateModel(
            name="Wiki",
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
                ("title", models.CharField(max_length=32, verbose_name="标题")),
                ("content", models.TextField(verbose_name="内容")),
                ("depth", models.IntegerField(default=1, verbose_name="深度")),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="web.project",
                        verbose_name="项目",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Wike",
        ),
    ]
