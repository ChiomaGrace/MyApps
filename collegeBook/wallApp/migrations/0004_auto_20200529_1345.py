# Generated by Django 3.0.6 on 2020-05-29 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0003_auto_20200529_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='userLikes',
            field=models.ManyToManyField(related_name='likeMessages', to='wallApp.User'),
        ),
    ]