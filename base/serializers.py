from rest_framework import serializers
from django.utils import timezone
from .models import *
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("password and confirm password doesn't match")

        # Validate the password using Django's built-in validators
        validate_password(password)

        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('password2', None)

        # Extract the password from validated_data
        password = validated_data.pop('password')

        user = User.objects.create(**validated_data)
        # Use Django's set_password method to hash and set the password
        user.set_password(password)
        # Save the user object with the hashed password
        user.save()
        return user


    

# Serializer for changing user password
class changePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=255, style={'input_type': 'password'}, write_only=True)
    new_password = serializers.CharField(required=True, max_length=255, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(required=True, max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')


         # Check if the old password matches the user's current password
        if not user.check_password(old_password):
            raise serializers.ValidationError('Old password is incorrect')

        # check that the new password and confirmation match
        if new_password != confirm_password:
            raise serializers.ValidationError("New Password and Confirm Password don't match")

        if len(new_password) <= 6:
            raise serializers.ValidationError("Weak Password")
        

        return attrs
    

        # Set the new password for the user
    def save(self):
        user = self.context.get('user')
        new_password = self.validated_data['new_password']

        # Set the new password for the user
        user.set_password(new_password)
        user.save()
       



# Serializer for resetting user password via email
class resetPasswordEmailSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True, max_length=50, style={'input_type':'email'}, write_only=True)



class VerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)



        

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'first_name', 'last_name', 'email', 'gender', 'profile_picture', 'phone_number', 'country', 'date_created', 'date_updated']
        read_only_fields = ['date_created', 'date_updated', 'first_name', 'last_name', 'email', 'user']

    



class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    error = serializers.CharField(required=False)

    




#Subcription Serializer
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'email', 'subscribed_at', 'is_subscribed']
        read_only_fields = ['id', 'subscribed_at']

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid email format")

        subscribed = Subscription.objects.filter(email=value).first()
        if subscribed:
            raise serializers.ValidationError("Email already registered, please use a different email")

        return value 

    def validate_is_subscribed(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Subscription status must be a boolean value")
        return value

    def create(self, validated_data):
        return Subscription.objects.create( **validated_data)