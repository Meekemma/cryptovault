from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings
from .models import WithdrawalRequest,Balance
from django_coinpayments.models import Payment
from django.contrib.auth import get_user_model
User = get_user_model()



@receiver(post_save, sender=WithdrawalRequest)
def send_withdrawal_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        company = 'BobbyGram'
        email_subject = 'Withdrawal Request Received'
        email_body = f"""
        Dear {user.first_name},

        Thank you for reaching out to {company}.

        We have received your withdrawal request for {instance.amount} {instance.crypto_currency if instance.crypto_currency else 'currency'}. Your request is currently pending review by our team. Please note the following details of your request:

        - Amount: {instance.amount} {instance.crypto_currency if instance.crypto_currency else 'currency'}
        - Requested Method: {'Bank' if instance.bank_name else 'Crypto'}
        - Bank Name (if applicable): {instance.bank_name}
        - Crypto Currency (if applicable): {instance.crypto_currency}
        - Crypto Address (if applicable): {instance.crypto_address}

        Our team will review your request shortly. You will receive another email once your withdrawal request has been processed or if we need any additional information from you.

        If you have any questions or need further assistance, please do not hesitate to contact our support team at [Support Email Address] or visit our help center at [Help Center URL].

        Thank you for your patience.

        Best regards,
        The {company} Team

        Important: This is an automated message. Please do not reply directly to this email. If you need assistance, contact us through the support channels mentioned above.
        """
        recipient_list = [user.email]

        try:
            email_message = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=recipient_list,
            )
            email_message.send(fail_silently=False)
        except Exception as e:
            # Log the exception for debugging
            print(f"Failed to send email: {str(e)}")



@receiver(post_save, sender=User)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)



@receiver(post_save, sender=Payment)
def update_user_balance(sender, instance, **kwargs):
    if instance.status == "PAID":
        # Get the user's balance and update it
        try:
            user_balance = instance.user.balance
            user_balance.update_balance()
        except Balance.DoesNotExist:
            # Create balance if it doesn't exist (fallback)
            Balance.objects.create(user=instance.user, balance=instance.amount_paid)

