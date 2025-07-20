from django.shortcuts import render,redirect
import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,parser_classes,renderer_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from django.conf import settings
from urllib.parse import urlencode
from django.http import HttpResponse
from django.contrib.auth import login,logout
from rest_framework.views import APIView
from .services import get_user_data
from .serializers import RegisterUserSerializer,changePasswordSerializer,UserProfileSerializer,AuthSerializer,SubscriptionSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .utils import send_code_to_user
from .models import User

from django.conf import settings

from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken




# Create your views here.




# Custom serializer for obtaining JWT token with additional claims
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['is_verified'] = user.is_verified
        

        return token
    
# validate method is overridden to add extra responses to the data returned by the parent class's validate method.
    def validate(self, attrs):
        # call validates the provided attributes using the parent class's validate method and returns the validated data.
        data = super().validate(attrs)

        # Add extra responses
        # Adds the user id to the response
        data.update({'user_id': self.user.id})
        full_name = f"{self.user.first_name} {self.user.last_name}"
        data.update({'full_name': full_name})
        data.update({'email': self.user.email})
        data.update({'is_verified': self.user.is_verified})

        return data

       
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class =MyTokenObtainPairSerializer 





class GoogleLoginApi(APIView):
    def get(self, request, *args, **kwargs):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        
        validated_data = auth_serializer.validated_data
        
        try:
            user_data = get_user_data(validated_data)  # This function needs to exchange the code for tokens
            user = User.objects.get(email=user_data['email'])
            login(request, user)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)


            response_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'id': user_data['id'],
                'email': user_data['email'],
                'first_name': user_data.get('first_name'),  # Use get() to handle cases where it's missing
                'last_name': user_data.get('last_name'),  # Adjust based on your data structure
                'is_verified': user.is_verified
            }

            if settings.BASE_APP_URL:
                # Add response data to query parameters for the redirect URL
                query_params = urlencode(response_data)
                redirect_url = f"{settings.BASE_APP_URL}?{query_params}"
                return redirect(redirect_url)
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



#logout view
class LogoutApi(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponse('200')




#Registration view
@api_view(['POST'])
def registerUsers(request):
    serializer = RegisterUserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()  # Save the user
        send_code_to_user(user.email)  # Send email to the user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    



#change password view
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def changePasswordView(request):
    """
    API endpoint to change the password of the authenticated user.
    """
    if request.method == 'PUT':
        serializer=changePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'detail': 'password changed successfully'}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to changed password", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    



#OTP VERIFICATION VIEW
@api_view(['POST'])
def code_verification(request):
    if request.method == 'POST':
        otp_code = request.data.get('code') # Extract the OTP code from the request data
        if not otp_code:
            # If OTP code is not provided, return a bad request response
            return Response({'message': 'Passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to find a OneTimePassword object with the provided OTP code
            user_code_obj = OneTimePassword.objects.get(code=otp_code)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True  # If the user is not verified, mark them as verified and save
                user.save()
                return Response({'message': 'Account email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Code is invalid, user already verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        except OneTimePassword.DoesNotExist:
            return Response({'message': 'Invalid passcode'}, status=status.HTTP_400_BAD_REQUEST)




#RESEND OTP VIEW
@api_view(['POST'])
def resend_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    send_result = send_code_to_user(user.email)
    if "Failed" in send_result:
        return Response({'error': send_result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Assuming the send_code_to_user function returns a success message on success
    if send_result == "OTP sent successfully":
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    else:
        # Handling any other unexpected response from the utility function
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    





@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])
def user_profile(request, user_id):
    """
    Retrieve, update, or partially update the profile of the authenticated user.
    """
    try:
        profile = UserProfile.objects.get(user_id=user_id, user=request.user)
    except UserProfile.DoesNotExist:
        return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT' or request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   





    




@api_view(['POST'])
def email_subscription(request):
    if request.method == 'POST':
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"detail": "Email Subcription was successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
