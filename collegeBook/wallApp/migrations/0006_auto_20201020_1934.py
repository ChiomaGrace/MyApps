# Generated by Django 2.2.4 on 2020-10-20 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0005_user_profilephoto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='birthday',
        ),
        migrations.AddField(
            model_name='user',
            name='birthdayDay',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='birthdayMonth',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='birthdayYear',
            field=models.IntegerField(null=True),
        ),
    ]
