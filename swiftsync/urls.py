"""
SwiftSync AI — Main URL Configuration

All endpoints:
  /admin/                    → Django admin panel
  /api/                      → All API routes (see api/urls.py)
  /api/token/                → POST: Login — get JWT access + refresh tokens
  /api/token/refresh/        → POST: Refresh access token using refresh token
  /api/auth/register/        → POST: Register a new user
  /api/auth/profile/         → GET/PUT: View or update your profile
  /api/resources/            → GET/POST: List or create resources
  /api/resources/{id}/       → GET/PUT/PATCH/DELETE: Manage one resource
  /api/resources/my/         → GET: Your donated resources
  /api/requests/             → GET/POST: List or create requests
  /api/requests/{id}/        → GET/PATCH/DELETE: Manage one request
  /api/requests/my/          → GET: Your submitted requests
  /api/requests/{id}/approve/ → PATCH: Approve a request (donors only)
  /api/requests/{id}/reject/  → PATCH: Reject a request (donors only)
  /api/stats/                → GET: Platform statistics
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # All API routes defined in api/urls.py
    path('api/', include('api.urls')),
]
