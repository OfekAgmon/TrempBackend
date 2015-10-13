from django.conf.urls import url, include
from rides import views
from rest_framework.routers import DefaultRouter


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'rides', views.RideViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'devices', views.DeviceViewSet)
router.register(r'usualRides', views.UsualRideViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-token-auth/', views.obtain_auth_token_and_user),
    url(r'^destinations/$', views.DestinationList.as_view()),
    url(r'^myRides/$', views.MyRides.as_view()),
]
