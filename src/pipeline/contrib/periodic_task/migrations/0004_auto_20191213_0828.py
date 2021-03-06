# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-12-13 08:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('periodic_task', '0003_auto_20191213_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodictaskhistory',
            name='priority',
            field=models.IntegerField(default=100, verbose_name='流程优先级'),
        ),
        migrations.AddField(
            model_name='periodictaskhistory',
            name='queue',
            field=models.CharField(default='', max_length=512, verbose_name='流程使用的队列名'),
        ),
    ]
