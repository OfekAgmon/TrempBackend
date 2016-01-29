from lib2to3.pgen2 import driver
from rides.models import Ride, Device, UsualRide, PendingRequest
from django.contrib.auth.models import User
from rides.serializers import UserSerializer, RideSerializer, DeviceSerializer, \
    UsualRideSerializer, PendingRequestPostSerializer, PendingRequestGetSerializer
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

class NotificationType(Enum):
    Joined_Ride = 0
    Accept_Join_Ride = 1
    Refuse_Join_Ride = 2
    Cancelled_Ride = 3

class SendNotificationResult(Enum):
    Error = 0
    Success = 1
    Driver_Not_Logged_In = 2



def sendNotification(message, notificationType, ride, related_user_id, toUser):
    try:
        driver_device=Device.objects.get(user=toUser)
    except Device.DoesNotExist:
        # driver is not logged in
        return SendNotificationResult.Driver_Not_Logged_In
    data = {
        "message": message,
        "type": notificationType.name,
        "ride_id": ride.id,
        "asking_user": related_user_id,
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
    # default_detail = "This ride is already full."
    default_detail = "ההסעה מלאה"

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
        if self.action == 'list':
            return Ride.objects.filter(leaving_date=datetime.date.today).exclude(driver=self.request.user)
        else:
            return Ride.objects.all()



    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)

    def destroy(self, request, *args, **kwargs):
        ride = self.get_object()
        if not ride.passengers.all():
            ride.delete()
            return Response({'message': "ההסעה בוטלה בהצלחה"}, status=status.HTTP_200_OK)
        else:
            for p in ride.passengers.all():
                message = "\u200F" + str(ride.driver.username) + " ביטל את ההסעה ל" + str(ride.destination)
                result = sendNotification(message, NotificationType.Cancelled_Ride, ride, 5, p)
                if result == SendNotificationResult.Success:
                    ride.delete()
                    return Response({'message': "ההסעה בוטלה בהצלחה"}, status=status.HTTP_200_OK)



    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticated],)
    def driverApproval(self, request, pk=None):
        try:
            asking_user_id = request.DATA.get('asking_user', '0')
            ride_id = request.DATA.get('ride_id', '0')
            askingUser = User.objects.get(id=asking_user_id)
        except User.DoesNotExist:
            # return HttpResponseBadRequest("asking user doesn't exists")
            return Response({'message': "המשתמש המבקש לא קיים"}, status=status.HTTP_400_BAD_REQUEST)

        ride = self.get_object()

        # sending notification back to user for approval
        # result = sendNotification("You are in "+str(ride.driver.username) + "'s ride! ", NotificationType.Accept_Join_Ride, ride, 5, askingUser)
        message = "\u200F" + str(ride.driver.username)+ " צירף אותך להסעה שלו! "
        result = sendNotification(message, NotificationType.Accept_Join_Ride, ride, 5, askingUser)
        if result == SendNotificationResult.Success:
            ride.passengers.add(askingUser)
            ride.num_of_spots = ride.num_of_spots - 1
            ride.save()
            instance = PendingRequest.objects.get(ride=ride_id, passenger=askingUser)
            instance.delete()
            return Response({'message': "האישור התקבל בהצלחה"}, status=status.HTTP_200_OK)



    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticated],)
    def driverRefuse(self, request, pk=None):
        try:
            asking_user_id = request.DATA.get('asking_user', '0')
            ride_id = request.DATA.get('ride_id', '0')
            askingUser = User.objects.get(id=asking_user_id)
        except User.DoesNotExist:
            return Response({'message': "המשתמש המבקש לא קיים"}, status=status.HTTP_400_BAD_REQUEST)

        ride = self.get_object()

        # sending notification back to user for approval
        # result = sendNotification(str(ride.driver.username) + " couldn't add you to his ride", NotificationType.Refuse_Join_Ride, ride, 5, askingUser)
        message = "\u200F" + str(ride.driver.username) + " לא יכל להוסיף אותך להסעה שלו "
        result = sendNotification(message, NotificationType.Refuse_Join_Ride, ride, 5, askingUser)

        if result == SendNotificationResult.Success:
            instance = PendingRequest.objects.get(ride=ride_id, passenger=askingUser)
            instance.delete()
            return Response({'message': "הסירוב התקבל בהצלחה"}, status=status.HTTP_200_OK)




    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticated],)
    def askToJoinRide(self, request, pk=None):
        ride = self.get_object()

        # Check if the the user who attempts to join the the driver
        if self.request.user == ride.driver:
            return Response({'message': "אתה הנהג של ההסעה הזו!"}, status=status.HTTP_400_BAD_REQUEST)


        # Check if there is a pending request to this ride from this user

        try:
            instance = PendingRequest.objects.get(ride=ride.id, passenger=self.request.user)
        except PendingRequest.DoesNotExist:
            instance = None

        if instance is not None:
            # return HttpResponseBadRequest("You already asked to join this ride")
            # return HttpResponseBadRequest({'message': "כבר ביקשת להצטרף להסעה הזו!"})
            return Response({'message': "כבר ביקשת להצטרף להסעה הזו!"}, status=status.HTTP_400_BAD_REQUEST)


        # Check if there is no more spots
        if ride.num_of_spots == 0:
            return Response({'message': "ההסעה מלאה!"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            my_rides = self.request.user.rides_as_passenger.all()

            # Check if user is already in this ride
            if ride in my_rides:
                return Response({'message': "אתה כבר נמצא בהסעה הזו!"}, status=status.HTTP_400_BAD_REQUEST)



            else:
                user_id = self.request.user.id
                user = User.objects.get(id=user_id)
                # result = sendNotification(str(user.username) + " wants to join your ride to " + str(ride.destination),
                #                           NotificationType.Joined_Ride, ride, user_id, ride.driver)
                message = "\u200F" + str(user.username) + " רוצה להצטרף להסעה שלך ל"+ str(ride.destination)
                result = sendNotification(message,
                                          NotificationType.Joined_Ride, ride, user_id, ride.driver)
                if result == SendNotificationResult.Success:
                    return Response({'message': "ביקשת להצטרף להסעה, אתה תקבל הודעה לאישור"}, status=status.HTTP_200_OK)

                if result == SendNotificationResult.Driver_Not_Logged_In:
                    return Response({'message': "ביקשת להצטרף להסעה, אתה תקבל הוסעה לאישור. הנהג כרגע לא מחובר"}, status=status.HTTP_200_OK)





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
            return Response({'message': "שם משתמש או סיסמא לא נכונים"}, status=status.HTTP_400_BAD_REQUEST)

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
            dev_id = request.DATA.get('device_id', '0')
            device = Device.objects.get(device_id=dev_id)
            device.user = user
            device.save()
            return Response({'token': token.key, 'user': user_serializer.data})
        else:
            return Response({'message': "משתמש מחובר ממכשיר אחר"}, status=status.HTTP_400_BAD_REQUEST)



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
        return Response(serializer.data, status=status.HTTP_200_OK)


class PendingRequestsViewSet(viewsets.ModelViewSet):
    queryset = PendingRequest.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'create':
            return PendingRequestPostSerializer
        if self.action == 'list':
            return PendingRequestGetSerializer


    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

    def get_queryset(self):
        return PendingRequest.objects.filter(driver=self.request.user)






