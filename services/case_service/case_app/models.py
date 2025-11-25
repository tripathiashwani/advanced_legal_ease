from django.db import models
from django.utils import timezone

# You will store only user_id because AuthService owns user data
class Case(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.IntegerField(null=True, blank=True)  # user_id from AuthService
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CaseParticipant(models.Model):
    ROLE_CHOICES = [
        ("CLIENT", "Client"),
        ("LAWYER", "Lawyer"),
        ("MEDIATOR", "Mediator"),
    ]

    case = models.ForeignKey(Case, related_name="participants", on_delete=models.CASCADE)
    user_id = models.IntegerField()  # from Auth Service
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user_id} -> {self.case.title}"


class CaseDocument(models.Model):
    case = models.ForeignKey(Case, related_name="documents", on_delete=models.CASCADE)
    uploaded_by = models.IntegerField()
    file_url = models.URLField()  # S3 URL or File Storage URL
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Doc for {self.case.title}"


class CaseActivity(models.Model):
    case = models.ForeignKey(Case, related_name="activities", on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    actor_id = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action} on {self.case.title}"
