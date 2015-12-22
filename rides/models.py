from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)

class UsualRide(models.Model):
    user = models.ForeignKey('auth.User', related_name='usual_rides')
    destination = models.CharField(max_length=100, default='')
    leaving_time=models.TimeField()
    num_of_spots=models.IntegerField()
    mid_destinations = models.CharField(max_length=100, default='')


class Ride(models.Model):
    driver = models.ForeignKey('auth.User', related_name='rides_as_driver')
    destination = models.CharField(max_length=100, default='')
    leaving_time=models.TimeField()
    leaving_date=models.DateField(default=datetime.date.today)
    num_of_spots=models.IntegerField()
    passengers=models.ManyToManyField('auth.User', related_name="rides_as_passenger")
    mid_destinations = models.CharField(max_length=100, default='')
    leaving_spot = models.CharField(max_length=100, default='')


class PendingRequest(models.Model):
    driver = models.ForeignKey('auth.User', related_name='driver_pending_requests')
    passenger = models.ForeignKey('auth.User', related_name='passenger_pending_requests')
    ride = models.ForeignKey(Ride)

@receiver(post_save, sender=User)
def handle_user_save(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
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


