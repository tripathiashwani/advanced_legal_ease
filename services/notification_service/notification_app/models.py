from django.db import models
import uuid

# Note: This service doesn't need its own User model
# It references users from the auth service via user_id (UUID)


class NotificationType(models.Model):
    """Types of notifications"""
    NOTIFICATION_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('IN_APP', 'In-App Notification'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    template_subject = models.CharField(max_length=200, blank=True)
    template_body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.type})"
    
    class Meta:
        verbose_name = "Notification Type"
        verbose_name_plural = "Notification Types"


class NotificationTemplate(models.Model):
    """Email/notification templates"""
    TEMPLATE_TYPES = [
        ('WELCOME', 'Welcome Email'),
        ('VERIFICATION', 'Email Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('HEARING_REMINDER', 'Hearing Reminder'),
        ('CASE_UPDATE', 'Case Update'),
        ('DOCUMENT_SHARED', 'Document Shared'),
        ('PAYMENT_CONFIRMATION', 'Payment Confirmation'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    html_body = models.TextField()
    text_body = models.TextField(blank=True)
    variables = models.JSONField(
        default=dict, 
        help_text="Available template variables as JSON"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.template_type}"
    
    class Meta:
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"


class Notification(models.Model):
    """Individual notification records"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=50, help_text="Reference to user from auth service")
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    html_message = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    
    # Tracking fields
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Metadata
    metadata = models.JSONField(default=dict, help_text="Additional data for the notification")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.notification_type} to {self.email} - {self.status}"
    
    def can_retry(self):
        return self.retry_count < self.max_retries and self.status == 'FAILED'
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']


class NotificationPreference(models.Model):
    """User notification preferences"""
    user_id = models.CharField(max_length=50, unique=True, help_text="Reference to user from auth service")
    email = models.EmailField()
    
    # Email preferences
    email_notifications = models.BooleanField(default=True)
    welcome_emails = models.BooleanField(default=True)
    hearing_reminders = models.BooleanField(default=True)
    case_updates = models.BooleanField(default=True)
    document_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    
    # SMS preferences
    sms_notifications = models.BooleanField(default=False)
    sms_urgent_only = models.BooleanField(default=True)
    
    # Push notification preferences
    push_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.email}"
    
    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"
