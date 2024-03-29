# Generated by Django 4.1.7 on 2023-03-01 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0013_wiki_delete_wike"),
    ]

    operations = [
        migrations.AddField(
            model_name="wiki",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="web.wiki",
                verbose_name="父文章",
            ),
        ),
    ]
