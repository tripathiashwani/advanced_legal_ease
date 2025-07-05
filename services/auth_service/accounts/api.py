# accounts/views.py
from .serializers import SignupSerializer,LoginSerializer
# from .kafka_producer import produce_event
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Publish to Kafka
        # produce_event(
        #     "user_signed_up",
        #     f"{user.id},{user.email}"
        # )
        return user

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # safe because .validate() sets it

        response = super().post(request, *args, **kwargs)

        # now you can produce the event:
        # produce_event(
        #     "user_logged_in",
        #     f"{user.id},{user.email}"
        # )

        return response
