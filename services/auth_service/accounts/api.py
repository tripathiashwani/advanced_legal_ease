# accounts/views.py
from .models import User, UserProfile
from .serializers import SignupSerializer,LoginSerializer, UserProfileSerializer
# from .kafka_producer import produce_event
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

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
        user = serializer.user  

        response = super().post(request, *args, **kwargs)

        # now you can produce the event:
        # produce_event(
        #     "user_logged_in",
        #     f"{user.id},{user.email}"
        # )

        return response



class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile