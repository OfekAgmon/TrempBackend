from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from rest_framework.authtoken.models import Token


class Destination(models.Model):
    name=models.CharField(max_length=30)

class UsualRide(models.Model):
    user = models.ForeignKey('auth.User', related_name='usual_rides')
    destination=models.ForeignKey(Destination, related_name='usual_rides_as_final_destination')
    leaving_time=models.TimeField()
    num_of_spots=models.IntegerField()
    mid_destinations=models.ManyToManyField(Destination, related_name='usual_rides_as_middle_destination')

class Ride(models.Model):
    driver = models.ForeignKey('auth.User', related_name='rides_as_driver')
    destination=models.ForeignKey(Destination, related_name='rides_as_final_destination')
    leaving_time=models.TimeField()
    leaving_date=models.DateField(default=datetime.date.today)
    num_of_spots=models.IntegerField()
    passengers=models.ManyToManyField('auth.User', related_name="rides_as_passenger")
    mid_destinations=models.ManyToManyField(Destination, related_name='rides_as_middle_destination')

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Device(models.Model):
    ANDROID = 1
    IPHONE = 2
    CHROME = 3
    OTHER = 4

    # DEVICE_CHOICES = ((ANDROID, 'Android'), (IPHONE, 'iPhone'), (CHROME,'Chrome'), (OTHER, 'Others'))

    device_id = models.CharField(unique = True, max_length = 1024, default='')
    # device_type = models.SmallIntegerField(choices = DEVICE_CHOICES)
    user = models.ForeignKey('auth.User', null=True)


