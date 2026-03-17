from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Resource, Request


# ─── User Serializers ───────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for displaying user info in nested responses."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    """Handles new user registration with password confirmation."""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="Confirm Password")

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2']
        read_only_fields = ['id']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


# ─── Resource Serializers ────────────────────────────────────────────────────

class ResourceSerializer(serializers.ModelSerializer):
    """Full resource serializer — used for create/update."""
    donor_username = serializers.CharField(source='donor.username', read_only=True)

    class Meta:
        model = Resource
        fields = [
            'id', 'donor', 'donor_username', 'title', 'category',
            'quantity', 'location', 'expiry_time', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'donor_username', 'created_at', 'updated_at']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value


class ResourceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing resources."""
    donor_username = serializers.CharField(source='donor.username', read_only=True)

    class Meta:
        model = Resource
        fields = ['id', 'title', 'category', 'quantity', 'location', 'status', 'donor_username']


# ─── Request Serializers ─────────────────────────────────────────────────────

class RequestSerializer(serializers.ModelSerializer):
    """Full request serializer — used for create/update."""
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    resource_title = serializers.CharField(source='resource.title', read_only=True)

    class Meta:
        model = Request
        fields = [
            'id', 'resource', 'resource_title', 'receiver', 'receiver_username',
            'status', 'message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'receiver_username', 'resource_title', 'created_at', 'updated_at']

    def validate(self, data):
        # Prevent requesting your own donated resource
        resource = data.get('resource')
        receiver = data.get('receiver')
        if resource and receiver and resource.donor == receiver:
            raise serializers.ValidationError("You cannot request your own donated resource.")

        # Prevent requesting unavailable resources
        if resource and resource.status != 'available':
            raise serializers.ValidationError(
                f"This resource is not available. Current status: {resource.status}"
            )
        return data
