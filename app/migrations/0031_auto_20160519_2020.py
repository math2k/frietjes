# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-19 20:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20160519_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='eatinggroup',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Company'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='foodprovider',
            name='type',
            field=models.CharField(choices=[(b'takeaway', b'Takeaway'), (b'restaurant', b'Restaurant'), (b'shop', b'Shop')], max_length=50),
        ),
    ]
