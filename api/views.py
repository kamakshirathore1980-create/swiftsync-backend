from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Request, Resource
from .serializers import (
    RegisterSerializer,
    RequestSerializer,
    ResourceListSerializer,
    ResourceSerializer,
    UserSerializer,
)

# ───────────────── AUTH ─────────────────

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ───────────────── RESOURCE ─────────────────

class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'location']
    search_fields = ['title', 'location']
    ordering_fields = ['created_at', 'quantity', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Resource.objects.select_related('donor')

    def get_serializer_class(self):
        return ResourceListSerializer if self.action == 'list' else ResourceSerializer

    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)

    def update(self, request, *args, **kwargs):
        resource = self.get_object()
        if resource.donor_id != request.user.id:
            return Response({"error": "You can only edit your own resources."}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        resource = self.get_object()
        if resource.donor_id != request.user.id:
            return Response({"error": "You can only delete your own resources."}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my(self, request):
        qs = Resource.objects.filter(donor=request.user).select_related('donor')
        return Response(ResourceSerializer(qs, many=True).data)

    @action(detail=True, methods=['patch'])
    def mark_claimed(self, request, pk=None):
        resource = self.get_object()

        if resource.donor_id != request.user.id:
            return Response({"error": "Only donor can mark as claimed"}, status=403)

        if resource.status == 'claimed':
            return Response({"error": "Already claimed"}, status=400)

        resource.status = 'claimed'
        resource.save(update_fields=['status', 'updated_at'])

        return Response({"message": "Resource marked as claimed"})


# ───────────────── REQUEST ─────────────────

class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    # ✅ ONLY used for list views (safe)
    def get_queryset(self):
        user = self.request.user
        return Request.objects.filter(
            Q(receiver=user) | Q(resource__donor=user)
        ).select_related('resource', 'receiver', 'resource__donor')

    # 🔥 FINAL SAFE OBJECT FETCH (NO UNION, NO .get())
    def get_object(self):
        pk = self.kwargs.get('pk')

        req = Request.objects.select_related(
            'resource', 'receiver', 'resource__donor'
        ).filter(pk=pk).first()

        if not req:
            raise NotFound("Request not found")

        user = self.request.user

        if req.receiver_id != user.id and req.resource.donor_id != user.id:
            raise NotFound("Request not found")

        return req

    # 🔥 VALIDATION (production safe)
    def perform_create(self, serializer):
        resource = serializer.validated_data.get('resource')

        if resource.donor_id == self.request.user.id:
            raise ValidationError({"error": "You cannot request your own resource."})

        if resource.status != 'available':
            raise ValidationError({"error": f"Resource not available: {resource.status}"})

        if Request.objects.filter(resource=resource, receiver=self.request.user).exists():
            raise ValidationError({"error": "Already requested this resource."})

        serializer.save(receiver=self.request.user)

    def destroy(self, request, *args, **kwargs):
        req = self.get_object()
        if req.receiver_id != request.user.id:
            return Response({"error": "You can only delete your own requests."}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def outgoing(self, request):
        qs = Request.objects.filter(receiver=request.user).select_related(
            'resource', 'receiver', 'resource__donor'
        )
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def incoming(self, request):
        qs = Request.objects.filter(resource__donor=request.user).select_related(
            'resource', 'receiver', 'resource__donor'
        )
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        with transaction.atomic():
            req = self.get_object()

            if req.resource.donor_id != request.user.id:
                return Response({"error": "Only donor can approve"}, status=403)

            if req.status != 'pending':
                return Response({"error": "Already processed"}, status=400)

            if req.resource.status != 'available':
                return Response({"error": "Resource not available"}, status=400)

            req.status = 'approved'
            req.save(update_fields=['status', 'updated_at'])

            req.resource.status = 'claimed'
            req.resource.save(update_fields=['status', 'updated_at'])

            Request.objects.filter(
                resource=req.resource,
                status='pending'
            ).exclude(pk=req.pk).update(status='rejected')

        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        req = self.get_object()

        if req.resource.donor_id != request.user.id:
            return Response({"error": "Only donor can reject"}, status=403)

        if req.status != 'pending':
            return Response({"error": "Already processed"}, status=400)

        req.status = 'rejected'
        req.save(update_fields=['status', 'updated_at'])

        return Response(self.get_serializer(req).data)


# ───────────────── STATS ─────────────────

class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "total_resources": Resource.objects.count(),
            "available_resources": Resource.objects.filter(status='available').count(),
            "claimed_resources": Resource.objects.filter(status='claimed').count(),
            "total_requests": Request.objects.count(),
            "pending_requests": Request.objects.filter(status='pending').count(),
            "approved_requests": Request.objects.filter(status='approved').count(),
            "rejected_requests": Request.objects.filter(status='rejected').count(),
        })