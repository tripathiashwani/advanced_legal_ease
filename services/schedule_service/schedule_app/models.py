from django.db import models
from django.utils import timezone


class Schedule(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("RESCHEDULED", "Rescheduled"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    case_id = models.IntegerField()  # From Case Service
    scheduled_by = models.IntegerField()  # Lawyer/Mediator user_id
    participants = models.JSONField()  # list of user_ids
    meeting_link = models.URLField(blank=True, null=True)  # From video_service
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Schedule for Case {self.case_id}"


class ScheduleActivity(models.Model):
    schedule = models.ForeignKey(Schedule, related_name="activities", on_delete=models.CASCADE)
    user_id = models.IntegerField()
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action} on schedule {self.schedule.id}"
