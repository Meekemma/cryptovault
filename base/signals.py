
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from .models import *
from django_rest_passwordreset.signals import reset_password_token_created
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import uuid

User = get_user_model()


def generate_referral_code():
    code = str(uuid.uuid4()).replace("-", "")[:7]
    return code


@receiver(post_save, sender=User)
def customer_Profile(sender, instance, created, *args, **kwargs):
    if created:
        # Ensure the necessary groups are created
        free_group, created = Group.objects.get_or_create(name='Free')
        
        # Add the user to the "Free" group by default
        instance.groups.add(free_group)

        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
            referral_code = generate_referral_code()
        )
        print('User Profile created for', instance.first_name)

        

@receiver(post_save, sender=User)
def update_Profile(sender, instance, created, *args, **kwargs):
    if not created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if created:
            print('User Profile was missing and has been created for existing user')
        else:
            profile.save()
            print('Profile updated!!!')





@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if not created and instance.is_verified and not instance._state.adding:
        # Prepare the context for the template
        context = {
            'get_full_name': instance.get_full_name,
            'email': instance.email
        }

        # Render the email subject, plain text, and HTML message
        subject = 'Welcome to Trexiz Limited'
        text_content = render_to_string('email/welcome_email.txt', context)
        html_content = render_to_string('email/welcome_email.html', context)

        # Create the email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL 
,
            to=[instance.email]
        )

        # Attach the HTML version
        email.attach_alternative(html_content, "text/html")

        # Add the required Postmark header
        email.extra_headers = {'X-PM-Message-Stream': 'outbound'}

        # Send the email
        email.send(fail_silently=False)






@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    try:
        # Context for the email
        custom_url_base = "https://www.trexiz.com/reset_password_confirm"
        context = {
            'current_user': reset_password_token.user,
            'first_name': reset_password_token.user.first_name,
            'email': reset_password_token.user.email,
            'reset_password_url': "{}?token={}".format(custom_url_base, reset_password_token.key)
        }


        # Render email content
        email_html_message = render_to_string('email/user_reset_password.html', context)
        email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

        # Send the email
        msg = EmailMultiAlternatives(
            "Password Reset for {title}".format(title="Reset Password For Account"),
            email_plaintext_message,
            settings.DEFAULT_FROM_EMAIL,
            [reset_password_token.user.email]
        )
        msg.attach_alternative(email_html_message, "text/html")

        # Add the required Postmark header
        msg.extra_headers = {'X-PM-Message-Stream': 'outbound'}

        msg.send()
    except Exception as e:
        # Log or handle the exception
        print(f"Failed to send password reset email: {e}")