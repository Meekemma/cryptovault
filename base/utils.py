import random
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .models import User, OneTimePassword
from django.utils import timezone

# from mailchimp_marketing import Client




def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

def send_code_to_user(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return "User does not exist"

    otp_code = generate_otp()
    current_site = "Geeks.com"
    email_subject = "One-time password for Email verification"
    email_body = f"Hi {user.first_name}, thanks for signing up on {current_site}. Please verify your email using this one-time password: {otp_code}"

    # Save OTP to the database
    otp_record, created = OneTimePassword.objects.update_or_create(
        user=user,
        defaults={'code': otp_code, 'created_at': timezone.now()}
    )

    # Send email
    try:
        send_email = EmailMessage(
            subject=email_subject, 
            body=email_body,
            from_email=settings.EMAIL_HOST_USER, 
            to=[email]
        )
        send_email.send(fail_silently=False)
    except Exception as e:
        return f"Failed to send email: {str(e)}"
    return "OTP sent successfully"




def send_welcome_email(user):
    try:
        email_subject = "Welcome to Our App!"
        email_body = f"Hi {user.first_name}, Thank you for joining our app. We appreciate your support."

        send_email = EmailMessage(
            subject=email_subject, 
            body=email_body,
            from_email=settings.EMAIL_HOST_USER, 
            to=[user.email]
        )
        send_email.send(fail_silently=False)
        return True
    except Exception as e:
        # Log or handle the error appropriately
        return False

def verify_otp(email, code):
    try:
        otp_record = OneTimePassword.objects.get(user__email=email, code=code)
        # Check if the OTP is expired (e.g., validity period of 30 minutes)
        if otp_record.created_at < timezone.now() - timezone.timedelta(minutes=30):
            return "expired"  # OTP has expired
        else:
            user = otp_record.user
            user.is_verified = True
            user.save()

            # Send welcome email if verification is successful
            if send_welcome_email(user):
                return "success"
            else:
                return "email_error"
    except OneTimePassword.DoesNotExist:
        return "invalid"
    except Exception as e:
        # Log or handle the error appropriately
        return "error"