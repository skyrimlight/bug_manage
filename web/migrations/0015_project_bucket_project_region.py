# Generated by Django 4.1.7 on 2023-03-02 09:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0014_wiki_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="bucket",
            field=models.CharField(default="xxx", max_length=128, verbose_name="cos桶"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="project",
            name="region",
            field=models.CharField(default="xxx", max_length=32, verbose_name="cos区域"),
            preserve_default=False,
        ),
    ]
