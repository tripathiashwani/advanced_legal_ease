from django.urls import path
from .views import CaseCreateView, CaseUpdateView, CaseDeleteView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("cases/create/", CaseCreateView.as_view(), name="case-create"),
    path("cases/<int:id>/update/", CaseUpdateView.as_view(), name="case-update"),
    path("cases/<int:id>/delete/", CaseDeleteView.as_view(), name="case-delete"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
