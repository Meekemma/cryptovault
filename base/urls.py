from django.urls import path
from . import views

from .views import LogoutApi,GoogleLoginApi
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/password_reset/request/', reset_password_request_token, name='reset_password_request_token'),
    path('api/password_reset/confirm/', reset_password_confirm, name='reset_password_confirm'),


    path('register/', views.registerUsers, name='register'),
    path('change-password/', views.changePasswordView, name='change-password'),
    path('verify_code/', views.code_verification, name='verify_code'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('user_profile/<int:user_id>/', views.user_profile, name='user_profile'),  
    path('email-subscription/', views.email_subscription, name='email-subscription'),
    path('google-login/', GoogleLoginApi.as_view(), name='google-login'),
    path('logout/', LogoutApi.as_view(), name='logout'),

]
