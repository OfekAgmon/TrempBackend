# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('leaving_time', models.TimeField()),
                ('num_of_spots', models.IntegerField()),
                ('destination', models.ForeignKey(to='rides.Destination', related_name='rides_as_final_destination')),
                ('driver', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='rides_as_driver')),
                ('mid_destinations', models.ManyToManyField(related_name='rides_as_middle_destination', to='rides.Destination')),
                ('passengers', models.ManyToManyField(related_name='rides_as_passenger', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
