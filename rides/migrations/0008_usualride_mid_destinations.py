# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0007_auto_20151118_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='usualride',
            name='mid_destinations',
            field=models.CharField(default='', max_length=100),
        ),
    ]
