from django.db import models
from django.contrib.auth.models import User


class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('books', 'Books'),
        ('clothes', 'Clothes'),
        ('devices', 'Devices'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('claimed', 'Claimed'),
        ('expired', 'Expired'),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_resources')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.IntegerField()
    location = models.CharField(max_length=255)
    expiry_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.category}) - {self.status}"

    class Meta:
        ordering = ['-created_at']


class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True, help_text="Optional message from the receiver")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request by {self.receiver.username} for {self.resource.title} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
        # Prevent a user from requesting the same resource twice
        unique_together = ('resource', 'receiver')
