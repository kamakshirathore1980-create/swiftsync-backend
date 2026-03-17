from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from .models import Resource, Request
from .serializers import (
    ResourceSerializer, ResourceListSerializer,
    RequestSerializer, RegisterSerializer, UserSerializer
)


# ─── Auth Views ───────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user account.
    No authentication required.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/auth/profile/   — View your profile
    PUT  /api/auth/profile/   — Update your profile
    Requires JWT authentication.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ─── Resource ViewSet ─────────────────────────────────────────────────────────

class ResourceViewSet(viewsets.ModelViewSet):
    """
    Provides full CRUD for Resources:
      GET    /api/resources/          — list all available resources
      POST   /api/resources/          — donate a new resource
      GET    /api/resources/{id}/     — get one resource
      PUT    /api/resources/{id}/     — update a resource (donor only)
      PATCH  /api/resources/{id}/     — partial update
      DELETE /api/resources/{id}/     — delete a resource (donor only)

    Extra actions:
      GET    /api/resources/my/       — list only your donated resources
      PATCH  /api/resources/{id}/mark_claimed/   — mark resource as claimed
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'location']
    search_fields = ['title', 'location']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']

    def get_queryset(self):
        return Resource.objects.select_related('donor').all()

    def get_serializer_class(self):
        # Use lighter serializer for list views
        if self.action == 'list':
            return ResourceListSerializer
        return ResourceSerializer

    def perform_create(self, serializer):
        # Automatically set the donor to the currently logged-in user
        serializer.save(donor=self.request.user)

    def update(self, request, *args, **kwargs):
        resource = self.get_object()
        # Only the original donor can update their resource
        if resource.donor != request.user:
            return Response(
                {"detail": "You can only edit your own donated resources."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        resource = self.get_object()
        if resource.donor != request.user:
            return Response(
                {"detail": "You can only delete your own donated resources."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my')
    def my_resources(self, request):
        """GET /api/resources/my/ — returns only the logged-in user's resources."""
        resources = Resource.objects.filter(donor=request.user)
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='mark_claimed')
    def mark_claimed(self, request, pk=None):
        """PATCH /api/resources/{id}/mark_claimed/ — mark resource as claimed."""
        resource = self.get_object()
        if resource.donor != request.user:
            return Response(
                {"detail": "Only the donor can mark a resource as claimed."},
                status=status.HTTP_403_FORBIDDEN
            )
        resource.status = 'claimed'
        resource.save()
        return Response({"detail": "Resource marked as claimed.", "status": resource.status})


# ─── Request ViewSet ──────────────────────────────────────────────────────────

class RequestViewSet(viewsets.ModelViewSet):
    """
    Provides full CRUD for Requests:
      GET    /api/requests/           — list all requests (filtered to user)
      POST   /api/requests/           — submit a new request
      GET    /api/requests/{id}/      — get one request
      PATCH  /api/requests/{id}/      — update status (donor approves/rejects)
      DELETE /api/requests/{id}/      — cancel a request

    Extra actions:
      GET    /api/requests/my/        — list only your submitted requests
      PATCH  /api/requests/{id}/approve/  — approve a request (donor only)
      PATCH  /api/requests/{id}/reject/   — reject a request (donor only)
    """
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        # Return requests where user is the receiver OR the donor of the resource
        return Request.objects.filter(
            receiver=user
        ).union(
            Request.objects.filter(resource__donor=user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically set receiver to the logged-in user
        serializer.save(receiver=self.request.user)

    def destroy(self, request, *args, **kwargs):
        req = self.get_object()
        if req.receiver != request.user:
            return Response(
                {"detail": "You can only cancel your own requests."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my')
    def my_requests(self, request):
        """GET /api/requests/my/ — returns only the logged-in user's submitted requests."""
        requests = Request.objects.filter(receiver=request.user)
        serializer = RequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        """PATCH /api/requests/{id}/approve/ — donor approves a request."""
        req = self.get_object()
        if req.resource.donor != request.user:
            return Response(
                {"detail": "Only the resource donor can approve requests."},
                status=status.HTTP_403_FORBIDDEN
            )
        req.status = 'approved'
        req.save()
        # Also mark the resource as claimed
        req.resource.status = 'claimed'
        req.resource.save()
        return Response({"detail": "Request approved. Resource marked as claimed."})

    @action(detail=True, methods=['patch'], url_path='reject')
    def reject(self, request, pk=None):
        """PATCH /api/requests/{id}/reject/ — donor rejects a request."""
        req = self.get_object()
        if req.resource.donor != request.user:
            return Response(
                {"detail": "Only the resource donor can reject requests."},
                status=status.HTTP_403_FORBIDDEN
            )
        req.status = 'rejected'
        req.save()
        return Response({"detail": "Request rejected."})


# ─── Stats View ───────────────────────────────────────────────────────────────

class StatsView(APIView):
    """
    GET /api/stats/
    Returns platform-wide summary statistics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = {
            "total_resources": Resource.objects.count(),
            "available_resources": Resource.objects.filter(status='available').count(),
            "claimed_resources": Resource.objects.filter(status='claimed').count(),
            "total_requests": Request.objects.count(),
            "pending_requests": Request.objects.filter(status='pending').count(),
            "fulfilled_requests": Request.objects.filter(status='fulfilled').count(),
            "total_donors": User.objects.filter(donated_resources__isnull=False).distinct().count(),
            "resources_by_category": {
                category: Resource.objects.filter(category=category).count()
                for category, _ in Resource.CATEGORY_CHOICES
            }
        }
        return Response(stats)
