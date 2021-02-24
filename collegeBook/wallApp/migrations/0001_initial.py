# Generated by Django 2.2.4 on 2021-02-21 16:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=255)),
                ('lastName', models.CharField(max_length=255)),
                ('birthdayMonth', models.CharField(max_length=30, null=True)),
                ('birthdayDay', models.IntegerField(null=True)),
                ('birthdayYear', models.IntegerField(null=True)),
                ('emailAddress', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('confirmPassword', models.CharField(max_length=255)),
                ('profilePic', models.ImageField(null=True, upload_to='submittedProfilePicImages/', verbose_name='')),
                ('profileHeader', models.CharField(default='', max_length=255)),
                ('notifications', models.IntegerField(default='0')),
                ('userCheckBox', models.BooleanField(default=False)),
                ('userUniversity', models.CharField(default='', max_length=255)),
                ('userHighSchool', models.CharField(default='', max_length=255)),
                ('userDormBuilding', models.CharField(default='', max_length=255)),
                ('userHomeTown', models.CharField(default='', max_length=255)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('friends', models.ManyToManyField(related_name='friendship', to='wallApp.User')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('likeMessageCount', models.IntegerField(default=0)),
                ('likeMessageCountMinusDisplayNames', models.IntegerField(default=0)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='wallApp.User')),
                ('userLikes', models.ManyToManyField(related_name='theLiker', to='wallApp.User')),
                ('userReceivesPost', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='postRecipient', to='wallApp.User')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='wallApp.Message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='wallApp.User')),
                ('userReceivesComment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commentee', to='wallApp.User')),
            ],
        ),
    ]