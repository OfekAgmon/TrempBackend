from rides.models import Ride, Destination, Device, UsualRide
from django.contrib.auth.models import User
from rides.serializers import UserSerializer, DestinationSerializer, RideSerializer, DeviceSerializer, UsualRideSerializer
from rest_framework.decorators import detail_route, list_route
from rides.permissions import IsCreationOrIsAuthenticated
from rides.permissions import IsGetOrIsAuthenticated
from rest_framework import viewsets
import requests
import datetime
from enum import Enum
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.http import HttpResponseBadRequest
from django.http import HttpResponse

class NotificationType(Enum):
    Joined_Ride = 0
    New_Ride_Available = 1

class SendNotificationResult(Enum):
    Error = 0
    Success = 1
    Driver_Not_Logged_In = 2

def sendNotification(message, notificationType, driver):
    try:
        driver_device=Device.objects.get(user=driver)
    except Device.DoesNotExist:
        # driver is not logged in
        return SendNotificationResult.Driver_Not_Logged_In
    data = {
        "message": message,
        "type": notificationType.name,
    }
    payload = {'to': driver_device.device_id, 'data': data, }
    r = requests.post("https://gcm-http.googleapis.com/gcm/send",
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'key=AIzaSyDUeGorbfKYPRbtM_UWHic6CWBQNFN9Gfs'
                        },
                json=payload)
    print(r.text)
    result = r.json().get('success')
    if result == SendNotificationResult.Success.value:
        return SendNotificationResult.Success
    if result == SendNotificationResult.Error.value:
        return SendNotificationResult.Error


class FullRideException(APIException):
    status_code = 409
    default_detail = "This ride is already full."

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @list_route(methods=['put'], permission_classes=[permissions.IsAuthenticated],)
    def attachUser(self, request):
        dev_id = request.DATA.get('device_id', '0')
        device = Device.objects.get(device_id=dev_id)
        device.user = self.request.user
        device.save()
        return Response(status=status.HTTP_200_OK)

    @list_route(methods=['put'], permission_classes=[permissions.IsAuthenticated],)
    def freeUser(self, request):
        device = Device.objects.get(user=self.request.user)
        device.user = None
        device.save()
        return Response(status=status.HTTP_200_OK)


class UsualRideViewSet(viewsets.ModelViewSet):
    queryset = UsualRide.objects.all()
    serializer_class = UsualRideSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return UsualRide.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Ride.objects.filter(leaving_date=datetime.date.today)

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)

    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticated],)
    def attach(self, request, pk=None):
        ride = self.get_object()

        # Check if the the user who attempts to join the the driver
        if self.request.user == ride.driver:
            return HttpResponseBadRequest("You are the ride's driver.")

        # Check if there is no more spots
        if ride.num_of_spots == 0:
            return HttpResponseBadRequest("Ride is already full.")
        else:
            my_rides = self.request.user.rides_as_passenger.all()

            # Check if user is already in this ride
            if ride in my_rides:
                return HttpResponseBadRequest("You are already in this ride.")
            else:

                result = sendNotification("someone joined your ride", NotificationType.Joined_Ride, ride.driver)

                if result == SendNotificationResult.Success:
                    ride.passengers.add(self.request.user)
                    ride.num_of_spots = ride.num_of_spots - 1
                    ride.save()
                    return HttpResponse("Joined ride succesfully")

                if result == SendNotificationResult.Driver_Not_Logged_In:
                    ride.passengers.add(self.request.user)
                    ride.num_of_spots = ride.num_of_spots - 1
                    ride.save()
                    return HttpResponse("Joined ride succesfully, driver is currently not logged in")



class UserViewSet(mixins.CreateModelMixin,
               mixins.RetrieveModelMixin,
               mixins.ListModelMixin,
               viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsCreationOrIsAuthenticated,)


class ObtainAuthTokenAndUser(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            # wrong username or password
            return HttpResponseBadRequest("Wrong username or password")
        user = serializer.validated_data['user']
        try:
            device_used = Device.objects.get(user=user)
        except Device.DoesNotExist:
            # user is logged in from another device
            device_used = None
        if device_used == None:
            # user is not logged in currently, login is OK
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user)
            return Response({'token': token.key, 'user': user_serializer.data})
        else:
            return HttpResponseBadRequest("User is logged in from another device")

obtain_auth_token_and_user = ObtainAuthTokenAndUser.as_view()


class MyRides(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user=self.request.user
        # get(leaving_time=datetime.date.today)
        driverRides = user.rides_as_driver.filter(leaving_date=datetime.date.today())
        passengerRides = user.rides_as_passenger.filter(leaving_date=datetime.date.today())
        rides = []
        for j in driverRides:
            rides.append(j)
        for i in passengerRides:
            rides.append(i)
        serializer = RideSerializer(rides, many=True)
        return Response(serializer.data)



class DestinationList(APIView):
    permission_classes = (IsGetOrIsAuthenticated,)

    def get(self, request):
        destinations = Destination.objects.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)





