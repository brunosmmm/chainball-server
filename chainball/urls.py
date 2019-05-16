"""chainball URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
import gamehistory.views
import player_registry.views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"tournaments", gamehistory.views.TournamentViewSet)
router.register(r"players", player_registry.views.PlayerViewSet)
router.register(r"seasons", gamehistory.views.SeasonViewSet)
router.register(r"games", gamehistory.views.GameViewSet)
router.register(r"events", gamehistory.views.GameEventViewSet)

urlpatterns = [
    path("gamehistory/", include("gamehistory.urls")),
    path("admin/", admin.site.urls),
    path("registry/", include("player_registry.urls")),
    path("api/", include(router.urls)),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
]
