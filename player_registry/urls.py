from django.contrib.auth.decorators import login_required
from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"players", views.PlayerViewSet)

# OAuth2 provider endpoints
urlpatterns = [
    path("", include(router.urls)),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
]
