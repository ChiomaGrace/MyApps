# Generated by Django 2.2.4 on 2021-01-15 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0016_auto_20210115_1552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='likedMessage',
        ),
        migrations.AddField(
            model_name='message',
            name='likedMessageCount',
            field=models.IntegerField(default=0),
        ),
    ]
