# Generated by Django 4.1.7 on 2023-02-28 11:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0006_alter_project_color"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ProjectPartner",
            new_name="ProjectUser",
        ),
    ]
