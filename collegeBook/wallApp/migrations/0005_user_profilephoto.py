# Generated by Django 2.2.4 on 2020-07-05 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallApp', '0004_auto_20200529_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profilePhoto',
            field=models.FileField(null=True, upload_to='images/', verbose_name=''),
        ),
    ]
