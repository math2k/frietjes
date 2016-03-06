# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-06 09:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20160228_2108'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=b'menus')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.FoodProvider')),
            ],
        ),
    ]