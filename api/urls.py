from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ResourceViewSet,
    RequestViewSet,
    RegisterView,
    ProfileView,
    StatsView,
    health_check,
)

router = DefaultRouter()
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'requests', RequestViewSet, basename='request')

urlpatterns = [
    path('', include(router.urls)),

    # AUTH
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # STATS
    path('stats/', StatsView.as_view(), name='stats'),

    # HEALTH CHECK
    path('health/', health_check, name='health'),
]
