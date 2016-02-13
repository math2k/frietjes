# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20160116_1015'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=300)),
            ],
        ),
        migrations.AddField(
            model_name='menuitemcategory',
            name='provider',
            field=models.ForeignKey(default=1, to='app.FoodProvider'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='provider',
            field=models.ForeignKey(default=1, to='app.FoodProvider'),
            preserve_default=False,
        ),
    ]
