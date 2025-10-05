# accounts/views.py
from .models import User, UserProfile
from .serializers import SignupSerializer,LoginSerializer, UserProfileSerializer
from .kafka_producer import produce_event
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        
       
        user_data = {
            'user_id': str(user.id),
            'email': user.email,
            'username': user.username,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat()
        }
        
       
        logger.info(f"User {user.email} created successfully. Attempting to publish Kafka event...")
        
        try:
           
            result = produce_event(
                "user_signed_up",
                json.dumps(user_data)
            )
            logger.info(f"Kafka produce_event returned: {result}")
            logger.info(f"User signup event published for user {user.email}")
        except Exception as e:
            logger.error(f"Failed to publish user signup event: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
        
        return user
    
    def create(self, request, *args, **kwargs):
        """Override create to provide custom response"""
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            return Response({
                'message': 'User created successfully. Welcome email will be sent shortly.',
                'user': response.data
            }, status=status.HTTP_201_CREATED)
        
        return response

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  

        response = super().post(request, *args, **kwargs)

        # Publish login event to Kafka
        if response.status_code == status.HTTP_200_OK:
            user_data = {
                'user_id': str(user.id),
                'email': user.email,
                'username': user.username,
                'user_type': user.user_type,
                'login_time': user.last_login.isoformat() if user.last_login else None
            }
            
            try:
                produce_event(
                    "user_logged_in",
                    json.dumps(user_data)
                )
                logger.info(f"User login event published for user {user.email}")
            except Exception as e:
                logger.error(f"Failed to publish user login event: {str(e)}")

        return response



class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class EmailVerificationView(generics.GenericAPIView):
    """View to handle email verification"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        verification_token = request.data.get('token')
        
        if not user_id or not verification_token:
            return Response({
                'error': 'User ID and verification token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            
            # In a real implementation, you would validate the token
            # For now, we'll just mark the user as verified
            if not user.is_verified:
                user.is_verified = True
                user.verification_date = timezone.now()
                user.save()
                
                # Publish verification event to Kafka
                user_data = {
                    'user_id': str(user.id),
                    'email': user.email,
                    'username': user.username,
                    'user_type': user.user_type,
                    'verified_at': user.verification_date.isoformat()
                }
                
                try:
                    produce_event(
                        "user_verified",
                        json.dumps(user_data)
                    )
                    logger.info(f"User verification event published for user {user.email}")
                except Exception as e:
                    logger.error(f"Failed to publish user verification event: {str(e)}")
                
                return Response({
                    'message': 'Email verified successfully. Welcome notification will be sent.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Email already verified'
                }, status=status.HTTP_200_OK)
                
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid user ID'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return Response({
                'error': 'Verification failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)