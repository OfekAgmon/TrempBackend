# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0008_usualride_mid_destinations'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='leaving_spot',
            field=models.CharField(max_length=100, default=''),
        ),
    ]
