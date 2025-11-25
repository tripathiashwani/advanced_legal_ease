from rest_framework import serializers
from .models import Case, CaseParticipant, CaseDocument, CaseActivity

class CaseParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseParticipant
        fields = "__all__"

class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = "__all__"

class CaseSerializer(serializers.ModelSerializer):
    participants = CaseParticipantSerializer(many=True, read_only=True)
    documents = CaseDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = "__all__"
