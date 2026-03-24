from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Resource, Request


# ─── User Serializers ─────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'password', 'password2'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


# ─── Resource Serializers ─────────────────────────────────────

class ResourceSerializer(serializers.ModelSerializer):
    donor = serializers.PrimaryKeyRelatedField(read_only=True)  # ✅ FIX
    donor_username = serializers.CharField(source='donor.username', read_only=True)

    class Meta:
        model = Resource
        fields = [
            'id',
            'donor',
            'donor_username',
            'title',
            'category',
            'quantity',
            'location',
            'expiry_time',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'donor',
            'donor_username',
            'created_at',
            'updated_at'
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class ResourceListSerializer(serializers.ModelSerializer):
    donor_username = serializers.CharField(source='donor.username', read_only=True)

    class Meta:
        model = Resource
        fields = [
            'id',
            'title',
            'category',
            'quantity',
            'location',
            'status',
            'donor_username'
        ]


# ─── Request Serializers ─────────────────────────────────────

class RequestSerializer(serializers.ModelSerializer):
    receiver = serializers.PrimaryKeyRelatedField(read_only=True)  # 🔥 FIX (IMPORTANT)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    resource_title = serializers.CharField(source='resource.title', read_only=True)

    class Meta:
        model = Request
        fields = [
            'id',
            'resource',
            'resource_title',
            'receiver',
            'receiver_username',
            'status',
            'message',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'receiver',
            'receiver_username',
            'resource_title',
            'created_at',
            'updated_at',
            'status'
        ]

    def validate(self, data):
        resource = data.get('resource')
        user = self.context['request'].user

        # ❌ Prevent self-request
        if resource and resource.donor == user:
            raise serializers.ValidationError("You cannot request your own resource.")

        # ❌ Prevent unavailable resource
        if resource and resource.status != 'available':
            raise serializers.ValidationError(
                f"Resource not available (status: {resource.status})"
            )

        return data