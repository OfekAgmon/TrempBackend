from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rides.models import Ride, Device, UsualRide, PendingRequest, UserProfile
from django.contrib.auth.models import User

class CreateableSlugRelatedField(serializers.SlugRelatedField):

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            return self.create_from_data(data)
        except (TypeError, ValueError):
            self.fail('invalid')

    def create_from_data(self, data):
        model = self.get_queryset().model
        return model.objects.create(**{self.slug_field: data})

class RideSerializer(serializers.ModelSerializer):

    # destination = CreateableSlugRelatedField(
    #     slug_field='name',
    #     queryset=Destination.objects.all()
    # )
    # mid_destinations = CreateableSlugRelatedField(
    #     slug_field='name',
    #     many=True,
    #     queryset=Destination.objects.all()
    # )
    driver = serializers.ReadOnlyField(source='driver.username')

    class Meta:
        model = Ride
        fields = ('id', 'driver', 'destination', 'leaving_time', 'leaving_date',
                  'num_of_spots', 'passengers', 'mid_destinations')
        read_only_fields = ('id', 'driver', 'passengers', 'leaving_date', )

class UsualRideSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UsualRide
        fields = ('user', 'destination', 'leaving_time', 'num_of_spots', 'mid_destinations')
        read_only_fields = ('user', )

class UserSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(source='userprofile.phone_number')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'phone_number', )
        read_only_fields = ('phone_number', )
        extra_kwargs = {'password': {'write_only': True}}

    def init(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        self.fields['username'].validators = []

    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            username=validated_data['username'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        user.userprofile.phone_number = self.initial_data["phone_number"]
        user.userprofile.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', )

class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('device_id', )
        read_only_fields = ('user', )


# PendingRequests Serizlizers


class PendingRequestPostSerializer(serializers.ModelSerializer):

    driver = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    passenger = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = PendingRequest
        fields = ('passenger', 'driver', 'ride', )
        read_only_fields = ('passenger',)


class PendingRequestGetSerializer(serializers.ModelSerializer):

    ride = RideSerializer()

    driver = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    passenger = UserSerializer()

    class Meta:
        model = PendingRequest
        fields = ('passenger', 'driver', 'ride', )
        read_only_fields = ('passenger',)



