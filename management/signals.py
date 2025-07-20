
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Contact,Referral
from django.contrib.auth import get_user_model
from base.models import UserProfile

User = get_user_model()



@receiver(post_save, sender=User)
def reward_referrer_after_verification(sender, instance, created, **kwargs):
    """
    Trigger referral bonus once user verifies their email.
    """
    if created:
        return 

    # Only proceed if the user just became verified
    if instance.is_verified:
        try:
            referee_profile = UserProfile.objects.get(user=instance)
            referral = Referral.objects.get(referee=referee_profile, status='pending')
            
            referral.status = 'earned'
            referral.bonus = 10.00 
            referral.save()

            print(f"Referral bonus granted to {referral.referrer} for verified referee {referral.referee}")

        except (UserProfile.DoesNotExist, Referral.DoesNotExist):
            # No referral or profile exists — nothing to do
            pass







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

