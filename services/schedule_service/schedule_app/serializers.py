from rest_framework import serializers
from .models import Schedule, ScheduleActivity


class ScheduleActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleActivity
        fields = "__all__"


class ScheduleSerializer(serializers.ModelSerializer):
    activities = ScheduleActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = "__all__"
