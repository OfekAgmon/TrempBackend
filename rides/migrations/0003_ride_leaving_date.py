# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0002_device'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='leaving_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
