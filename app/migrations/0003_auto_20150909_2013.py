# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_userorder_paid'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItemCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('order', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='userorder',
            name='notes',
            field=models.TextField(default=b'', blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='category',
            field=models.ForeignKey(default=1, to='app.MenuItemCategory'),
            preserve_default=False,
        ),
    ]
