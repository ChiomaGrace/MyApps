# Generated by Django 2.2.4 on 2021-01-19 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0020_friendlist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendlist',
            old_name='userAccount',
            new_name='loggedInUser',
        ),
    ]