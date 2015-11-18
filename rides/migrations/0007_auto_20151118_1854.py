# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0006_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usualride',
            name='mid_destinations',
        ),
        migrations.AlterField(
            model_name='ride',
            name='destination',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.RemoveField(
            model_name='ride',
            name='mid_destinations',
        ),
        migrations.AddField(
            model_name='ride',
            name='mid_destinations',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='usualride',
            name='destination',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.DeleteModel(
            name='Destination',
        ),
    ]
