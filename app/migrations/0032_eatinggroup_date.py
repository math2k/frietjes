# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-21 20:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_auto_20160519_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='eatinggroup',
            name='date',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2016, 5, 21, 20, 29, 5, 643464, tzinfo=utc)),
            preserve_default=False,
        ),
    ]