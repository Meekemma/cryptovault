
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






@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    context = {
        'current_user': reset_password_token.user,
        'first_name': reset_password_token.user.first_name,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
    }


    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Reset Password For Account"),
        # message:
        email_plaintext_message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()