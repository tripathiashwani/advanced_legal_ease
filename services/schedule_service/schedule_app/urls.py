from .views import (
    ScheduleCreateView,
    ScheduleUpdateView,
    ScheduleDeleteView,
    ScheduleListByCaseView,
    ScheduleDetailView
)
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView




urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("schedule/create/", ScheduleCreateView.as_view(), name="schedule-create"),
    path("schedule/<int:id>/", ScheduleDetailView.as_view(), name="schedule-detail"),
    path("schedule/<int:id>/update/", ScheduleUpdateView.as_view(), name="schedule-update"),
    path("schedule/<int:id>/delete/", ScheduleDeleteView.as_view(), name="schedule-delete"),
    path("schedule/case/<int:case_id>/", ScheduleListByCaseView.as_view(), name="schedule-by-case"),
]
