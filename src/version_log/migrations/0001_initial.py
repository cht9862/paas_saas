# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-16 15:30


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VersionLogVisited',
            fields=[
                ('username', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='用户名')),
                ('visited_version', models.CharField(max_length=20, verbose_name='访问版本')),
            ],
            options={
                'verbose_name': '版本日志访问记录',
                'verbose_name_plural': '版本日志访问记录',
            },
        ),
    ]
