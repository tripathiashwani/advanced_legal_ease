# accounts/urls.py
from django.urls import path

from .api import LoginView, SignupView, ProfileView, EmailVerificationView
from rest_framework_simplejwt.views import TokenRefreshView
from .api import UploadPDFView, ChatWithPDFView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    # path('profile/details/', UserProfileDetailView.as_view(), name='profile_details'),
    path("upload-pdf/", UploadPDFView.as_view()),
    path("chat/", ChatWithPDFView.as_view()),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

