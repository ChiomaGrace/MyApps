# Generated by Django 2.2.4 on 2021-02-03 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='listOfFriends',
            new_name='friends',
        ),
    ]