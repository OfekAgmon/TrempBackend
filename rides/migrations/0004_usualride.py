# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rides', '0003_ride_leaving_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsualRide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('leaving_time', models.TimeField()),
                ('num_of_spots', models.IntegerField()),
                ('destination', models.ForeignKey(to='rides.Destination', related_name='usual_rides_as_final_destination')),
                ('mid_destinations', models.ManyToManyField(related_name='usual_rides_as_middle_destination', to='rides.Destination')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='usual_rides')),
            ],
        ),
    ]
