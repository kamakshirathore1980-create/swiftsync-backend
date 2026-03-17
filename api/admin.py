from django.contrib import admin
from .models import Resource, Request


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'quantity', 'location', 'status', 'donor', 'created_at']
    list_filter = ['category', 'status']
    search_fields = ['title', 'location', 'donor__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['resource', 'receiver', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['resource__title', 'receiver__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
