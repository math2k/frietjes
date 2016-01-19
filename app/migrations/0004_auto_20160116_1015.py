# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20150909_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_person',
            field=models.ForeignKey(related_name='delivery_person', blank=True, to='app.UserOrder', null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
