# Generated by Django 2.2.4 on 2021-02-21 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='userCheckBox',
            field=models.BooleanField(),
        ),
    ]