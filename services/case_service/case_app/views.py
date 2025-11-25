from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Case
from .serializers import CaseSerializer
logger = __import__('logging').getLogger(__name__)

# CREATE CASE
class CaseCreateView(generics.CreateAPIView):
    logger.info("CaseCreateView initialized")
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)


# UPDATE CASE
class CaseUpdateView(generics.UpdateAPIView):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = "id"


# DELETE CASE
class CaseDeleteView(generics.DestroyAPIView):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = "id"
