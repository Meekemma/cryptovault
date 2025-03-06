from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Balance

@receiver(post_save, sender=Payment)
def update_user_balance(sender, instance, **kwargs):
    """ Update user's balance when a payment is marked as completed. """
    if instance.status == "completed":
        balance, created = Balance.objects.get_or_create(user=instance.user)
        balance.update_balance()  # Call the update method


