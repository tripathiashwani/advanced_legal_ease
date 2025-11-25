from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Schedule, ScheduleActivity
from .serializers import ScheduleSerializer

# CREATE SCHEDULE
class ScheduleCreateView(generics.CreateAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        schedule = serializer.save(scheduled_by=self.request.user.id)

        # log activity
        ScheduleActivity.objects.create(
            schedule=schedule,
            user_id=self.request.user.id,
            action="Schedule created"
        )


# UPDATE SCHEDULE
class ScheduleUpdateView(generics.UpdateAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        ScheduleActivity.objects.create(
            schedule=self.get_object(),
            user_id=request.user.id,
            action="Schedule updated"
        )

        return response


# DELETE SCHEDULE
class ScheduleDeleteView(generics.DestroyAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def perform_destroy(self, instance):
        ScheduleActivity.objects.create(
            schedule=instance,
            user_id=self.request.user.id,
            action="Schedule deleted"
        )
        super().perform_destroy(instance)


# LIST SCHEDULES BY CASE
class ScheduleListByCaseView(generics.ListAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        case_id = self.kwargs["case_id"]
        return Schedule.objects.filter(case_id=case_id)


# GET DETAILS OF A SPECIFIC SCHEDULE
class ScheduleDetailView(generics.RetrieveAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
