
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Contact
from django.contrib.auth import get_user_model

User = get_user_model()




@receiver(post_save, sender=Contact)
def contact_submssion(sender, instance, created, *args, **kwargs):
    if created:
        # Send email to user
        subject = 'Thank you for contacting us!'
        message = 'This is a confirmation that we have received your message.'
        from_email = settings.EMAIL_HOST_USER
        to_email = instance.email 


        send_mail(subject, message, from_email, [to_email])

        admins = User.objects.filter(is_staff=True, is_superuser=True)
        admin_emails = [admin.email for admin in admins]

        subject_admin = 'New contact form submission'
        message_admin = f'A new contact form was submitted by {instance.name}.'
        send_mail(subject_admin, message_admin, from_email, admin_emails)

